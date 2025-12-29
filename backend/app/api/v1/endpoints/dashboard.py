#!/usr/bin/env python3
"""
Dashboard endpoints for CRM analytics and AI-powered insights
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, extract
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import calendar
import asyncio

from app.core.database import get_db, get_async_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.models.tenant import User, Tenant
from app.models.crm import Customer, CustomerStatus, Contact
from app.models.leads import Lead, LeadStatus
from app.models.quotes import Quote, QuoteStatus
from app.models.opportunities import Opportunity, OpportunityStage
from app.models.helpdesk import Ticket, TicketStatus
from sqlalchemy.exc import DBAPIError
from app.models.sla_compliance import SLAComplianceRecord, SLABreachAlert
from app.services.ai_analysis_service import AIAnalysisService
from app.core.api_keys import get_api_keys
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardStats(BaseModel):
    total_discovery: int
    total_leads: int
    total_prospects: int
    total_opportunities: int
    total_customers: int
    total_cold_leads: int
    total_inactive: int
    total_quotes: int
    quotes_pending: int
    quotes_accepted: int
    total_revenue: float
    avg_deal_value: float
    conversion_rate: float
    # Opportunity metrics
    active_opportunities: int
    opportunities_qualified: int
    opportunities_proposal_sent: int
    opportunities_closed_won: int
    opportunities_total_value: float
    # Lifecycle distribution
    lifecycle_distribution: Dict[str, int]
    # SLA metrics
    sla_compliance_rate: float
    sla_active_breaches: int
    sla_tickets_at_risk: int
    sla_total_tickets: int


class ConversionFunnelItem(BaseModel):
    status: str
    count: int
    percentage: float
    color: str


class PipelineStageItem(BaseModel):
    stage: str
    count: int
    total_value: float
    percentage: float


class RecentActivity(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    icon: str


class MonthlyTrend(BaseModel):
    month: str
    new_leads: int
    converted: int
    revenue: float


class AIInsight(BaseModel):
    type: str
    title: str
    description: str
    priority: str


class DashboardResponse(BaseModel):
    stats: DashboardStats
    conversion_funnel: List[ConversionFunnelItem]
    pipeline_stages: List[PipelineStageItem]
    recent_activity: List[RecentActivity]
    monthly_trends: List[MonthlyTrend]
    ai_insights: List[AIInsight]
    top_leads: List[Dict[str, Any]]


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get comprehensive dashboard data
    
    PERFORMANCE: Uses AsyncSession and parallel queries to minimize response time.
    All independent queries run in parallel using asyncio.gather.
    """
    
    try:
        tenant_id = current_tenant.id
        
        # OPTIMIZATION: Combine customer count queries into a single GROUP BY query
        customer_counts_query = await db.execute(
            select(
                Customer.status,
                func.count(Customer.id).label('count')
            ).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.is_deleted == False
                )
            ).group_by(Customer.status)
        )
        customer_counts = {row.status: row.count for row in customer_counts_query}
        
        # Extract counts by status (default to 0 if status not found)
        leads_count = customer_counts.get(CustomerStatus.LEAD, 0)
        prospects_count = customer_counts.get(CustomerStatus.PROSPECT, 0)
        opportunities_count = customer_counts.get(CustomerStatus.OPPORTUNITY, 0)
        customers_count = customer_counts.get(CustomerStatus.CUSTOMER, 0)
        cold_leads_count = customer_counts.get(CustomerStatus.COLD_LEAD, 0)
        inactive_count = customer_counts.get(CustomerStatus.INACTIVE, 0)
        lost_count = customer_counts.get(CustomerStatus.LOST, 0)
        
        # CRITICAL OPTIMIZATION: Run ALL independent queries in parallel
        # Create all query tasks first, then execute them all together
        discovery_task = db.execute(
            select(func.count(Lead.id)).where(
                and_(
                    Lead.tenant_id == tenant_id,
                    Lead.is_deleted == False
                )
            )
        )
        
        # Quote queries (handle missing table gracefully)
        quotes_total_task = db.execute(select(func.count(Quote.id)).where(
            and_(
                Quote.tenant_id == tenant_id,
                Quote.is_deleted == False
            )
        ))
        quotes_pending_task = db.execute(select(func.count(Quote.id)).where(
            and_(
                Quote.tenant_id == tenant_id,
                Quote.is_deleted == False,
                or_(
                    Quote.status == QuoteStatus.DRAFT,
                    Quote.status == QuoteStatus.SENT
                )
            )
        ))
        quotes_accepted_task = db.execute(select(func.count(Quote.id)).where(
            and_(
                Quote.tenant_id == tenant_id,
                Quote.status == QuoteStatus.ACCEPTED,
                Quote.is_deleted == False
            )
        ))
        revenue_task = db.execute(select(func.sum(Quote.total_amount)).where(
            and_(
                Quote.tenant_id == tenant_id,
                Quote.status == QuoteStatus.ACCEPTED,
                Quote.is_deleted == False
            )
        ))
        
        # Opportunity queries (handle missing table gracefully)
        active_opp_task = db.execute(select(func.count(Opportunity.id)).where(
            and_(
                Opportunity.tenant_id == tenant_id,
                Opportunity.is_deleted == False,
                ~Opportunity.stage.in_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST])
            )
        ))
        qualified_task = db.execute(select(func.count(Opportunity.id)).where(
            and_(
                Opportunity.tenant_id == tenant_id,
                Opportunity.stage == OpportunityStage.QUALIFIED,
                Opportunity.is_deleted == False
            )
        ))
        proposal_task = db.execute(select(func.count(Opportunity.id)).where(
            and_(
                Opportunity.tenant_id == tenant_id,
                Opportunity.stage == OpportunityStage.PROPOSAL_SENT,
                Opportunity.is_deleted == False
            )
        ))
        closed_won_task = db.execute(select(func.count(Opportunity.id)).where(
            and_(
                Opportunity.tenant_id == tenant_id,
                Opportunity.stage == OpportunityStage.CLOSED_WON,
                Opportunity.is_deleted == False
            )
        ))
        opp_value_task = db.execute(select(func.sum(Opportunity.estimated_value)).where(
            and_(
                Opportunity.tenant_id == tenant_id,
                Opportunity.is_deleted == False,
                Opportunity.estimated_value.isnot(None)
            )
        ))
        
        # Pipeline stage queries (all stages in parallel)
        stage_labels = ["Qualified", "Scoping", "Proposal Sent", "Negotiation", "Verbal Yes", "Closed Won"]
        stages = [
            OpportunityStage.QUALIFIED,
            OpportunityStage.SCOPING,
            OpportunityStage.PROPOSAL_SENT,
            OpportunityStage.NEGOTIATION,
            OpportunityStage.VERBAL_YES,
            OpportunityStage.CLOSED_WON
        ]
        pipeline_stage_tasks = [
            db.execute(select(func.count(Opportunity.id), func.sum(Opportunity.estimated_value)).where(
                and_(
                    Opportunity.tenant_id == tenant_id,
                    Opportunity.stage == stage,
                    Opportunity.is_deleted == False
                )
            )) for stage in stages
        ]
        
        # Recent customers query - OPTIMIZED: Only select columns needed for dashboard
        recent_customers_task = db.execute(
            select(
                Customer.id,
                Customer.company_name,
                Customer.status,
                Customer.created_at
            ).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.is_deleted == False
                )
            ).order_by(Customer.created_at.desc()).limit(5)
        )
        
        # Monthly trends queries (all 6 months in parallel)
        now = datetime.utcnow()
        month_trend_tasks = []
        month_starts = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            month_starts.append(month_start)
            
            # Create tasks for each month's queries
            month_leads_task = db.execute(select(func.count(Lead.id)).where(
                and_(
                    Lead.tenant_id == tenant_id,
                    Lead.created_at >= month_start,
                    Lead.created_at <= month_end,
                    Lead.is_deleted == False
                )
            ))
            month_converted_task = db.execute(select(func.count(Customer.id)).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.status == CustomerStatus.CUSTOMER,
                    Customer.is_deleted == False,
                    Customer.created_at >= month_start,
                    Customer.created_at <= month_end
                )
            ))
            month_revenue_task = db.execute(select(func.sum(Quote.total_amount)).where(
                and_(
                    Quote.tenant_id == tenant_id,
                    Quote.status == QuoteStatus.ACCEPTED,
                    Quote.is_deleted == False,
                    Quote.created_at >= month_start,
                    Quote.created_at <= month_end
                )
            ))
            month_trend_tasks.append((month_leads_task, month_converted_task, month_revenue_task))
        
        # Top leads query - OPTIMIZED: Only select columns needed for dashboard
        top_leads_task = db.execute(
            select(
                Customer.id,
                Customer.company_name,
                Customer.status,
                Customer.lead_score,
                Customer.business_sector
            ).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.is_deleted == False,
                    Customer.status.in_([CustomerStatus.LEAD, CustomerStatus.PROSPECT, CustomerStatus.OPPORTUNITY]),
                    Customer.lead_score >= 70
                )
            ).order_by(Customer.lead_score.desc()).limit(5)
        )
        
        # SLA metrics queries (handle missing table gracefully)
        sla_total_task = db.execute(select(func.count(Ticket.id)).where(
            and_(
                Ticket.tenant_id == tenant_id,
                Ticket.sla_policy_id.isnot(None),
                ~Ticket.status.in_([TicketStatus.CLOSED, TicketStatus.RESOLVED])
            )
        ))
        sla_breaches_task = db.execute(select(func.count(Ticket.id)).where(
            and_(
                Ticket.tenant_id == tenant_id,
                or_(
                    Ticket.sla_first_response_breached == True,
                    Ticket.sla_resolution_breached == True
                )
            )
        ))
        
        # Execute ALL queries in parallel using asyncio.gather
        # pipeline_stage_tasks is already a list of coroutines, add directly
        # month_trend_tasks is a list of tuples (month_leads_task, month_converted_task, month_revenue_task), flatten it
        all_tasks = [
            discovery_task,
            quotes_total_task, quotes_pending_task, quotes_accepted_task, revenue_task,
            active_opp_task, qualified_task, proposal_task, closed_won_task, opp_value_task,
            recent_customers_task,
            top_leads_task,
            sla_total_task, sla_breaches_task
        ] + pipeline_stage_tasks + \
          [task for month_tuple in month_trend_tasks for task in month_tuple]
        
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Debug: Log expected vs actual result count
        expected_count = len(all_tasks)
        actual_count = len(results)
        if expected_count != actual_count:
            logger.error(f"Result count mismatch: expected {expected_count}, got {actual_count}")
            raise HTTPException(
                status_code=500,
                detail=f"Dashboard query error: expected {expected_count} results, got {actual_count}"
            )
        
        # Process results
        # IMPORTANT: Process results in the SAME ORDER as all_tasks list
        result_idx = 0
        
        # Discovery (result_idx 0)
        discovery_result = results[result_idx]
        result_idx += 1
        discovery_count = discovery_result.scalar() or 0 if not isinstance(discovery_result, Exception) else 0
        
        # Quotes (result_idx 1-4)
        quotes_total_result = results[result_idx]
        quotes_pending_result = results[result_idx + 1]
        quotes_accepted_result = results[result_idx + 2]
        revenue_result = results[result_idx + 3]
        result_idx += 4
        
        total_quotes = quotes_total_result.scalar() or 0 if not isinstance(quotes_total_result, Exception) else 0
        quotes_pending = quotes_pending_result.scalar() or 0 if not isinstance(quotes_pending_result, Exception) else 0
        quotes_accepted = quotes_accepted_result.scalar() or 0 if not isinstance(quotes_accepted_result, Exception) else 0
        revenue_value = revenue_result.scalar() if not isinstance(revenue_result, Exception) else None
        total_revenue = float(revenue_value) if revenue_value else 0.0
        
        # Opportunities (result_idx 5-9)
        active_opp_result = results[result_idx]
        qualified_result = results[result_idx + 1]
        proposal_result = results[result_idx + 2]
        closed_won_result = results[result_idx + 3]
        opp_value_result = results[result_idx + 4]
        result_idx += 5
        
        active_opportunities = active_opp_result.scalar() or 0 if not isinstance(active_opp_result, Exception) else 0
        opportunities_qualified = qualified_result.scalar() or 0 if not isinstance(qualified_result, Exception) else 0
        opportunities_proposal_sent = proposal_result.scalar() or 0 if not isinstance(proposal_result, Exception) else 0
        opportunities_closed_won = closed_won_result.scalar() or 0 if not isinstance(closed_won_result, Exception) else 0
        opp_value = opp_value_result.scalar() if not isinstance(opp_value_result, Exception) else None
        opportunities_total_value = float(opp_value) if opp_value else 0.0
        
        # Recent customers (result_idx 10)
        recent_customers_result = results[result_idx]
        result_idx += 1
        recent_customers_rows = recent_customers_result.all() if not isinstance(recent_customers_result, Exception) else []
        
        recent_activity = []
        for row in recent_customers_rows:
            # Row tuple: (id, company_name, status, created_at)
            customer_id, company_name, status, created_at = row
            recent_activity.append(RecentActivity(
                id=str(customer_id),
                type="customer",
                title=f"New {status.value if hasattr(status, 'value') else status}",
                description=company_name,
                timestamp=created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
                icon="user-plus"
            ))
        
        # Top leads (result_idx 11)
        top_leads_result = results[result_idx]
        result_idx += 1
        top_leads_rows = top_leads_result.all() if not isinstance(top_leads_result, Exception) else []
        
        top_leads = []
        for row in top_leads_rows:
            # Row tuple: (id, company_name, status, lead_score, business_sector)
            lead_id, company_name, status, lead_score, business_sector = row
            top_leads.append({
                "id": str(lead_id),
                "company_name": company_name,
                "status": status.value if hasattr(status, 'value') else str(status),
                "lead_score": lead_score or 0,
                "business_sector": business_sector.value if business_sector and hasattr(business_sector, 'value') else None
            })
        
        # SLA metrics (result_idx 12-13)
        sla_total_result = results[result_idx]
        sla_breaches_result = results[result_idx + 1]
        result_idx += 2
        
        sla_total_tickets = sla_total_result.scalar() or 0 if not isinstance(sla_total_result, Exception) else 0
        sla_active_breaches = sla_breaches_result.scalar() or 0 if not isinstance(sla_breaches_result, Exception) else 0
        sla_tickets_at_risk = 0  # Can be calculated separately if needed
        sla_compliance_rate = ((sla_total_tickets - sla_active_breaches) / sla_total_tickets * 100) if sla_total_tickets > 0 else 100.0
        
        # Pipeline stages (result_idx 14-19) - 6 stages
        # Each pipeline_stage_tasks query returns ONE result with TWO values (count, sum)
        pipeline_stages = []
        total_pipeline_value = 0.0
        for idx, stage in enumerate(stages):
            stage_result = results[result_idx]
            result_idx += 1
            
            if not isinstance(stage_result, Exception):
                row = stage_result.first()
                if row:
                    count = row[0] if row[0] is not None else 0
                    value = float(row[1]) if row[1] is not None else 0.0
                else:
                    count = 0
                    value = 0.0
                total_pipeline_value += value
                
                pipeline_stages.append(PipelineStageItem(
                    stage=stage_labels[idx],
                    count=count,
                    total_value=value,
                    percentage=0.0
                ))
        
        # Calculate pipeline percentages
        if pipeline_stages:
            for stage in pipeline_stages:
                stage.percentage = (stage.total_value / total_pipeline_value * 100) if total_pipeline_value > 0 else 0.0
        
        # Monthly trends (result_idx 20-37) - 6 months * 3 tasks = 18 results
        monthly_trends = []
        for idx, (month_start, month_tasks) in enumerate(zip(month_starts, month_trend_tasks)):
            # Safety check: ensure we have enough results
            if result_idx + 2 >= len(results):
                logger.warning(f"Not enough results for monthly trends at index {result_idx}, total results: {len(results)}")
                break
            
            month_leads_result = results[result_idx]
            month_converted_result = results[result_idx + 1]
            month_revenue_result = results[result_idx + 2]
            result_idx += 3
            
            new_leads = month_leads_result.scalar() or 0 if not isinstance(month_leads_result, Exception) else 0
            converted = month_converted_result.scalar() or 0 if not isinstance(month_converted_result, Exception) else 0
            month_revenue_val = month_revenue_result.scalar() if not isinstance(month_revenue_result, Exception) else None
            month_revenue = float(month_revenue_val) if month_revenue_val else 0.0
            
            month_name = calendar.month_abbr[month_start.month]
            monthly_trends.append(MonthlyTrend(
                month=f"{month_name} {month_start.year}",
                new_leads=new_leads,
                converted=converted,
                revenue=month_revenue
            ))
        
        # Calculate derived metrics
        lifecycle_distribution = {
            "LEAD": leads_count,
            "PROSPECT": prospects_count,
            "CUSTOMER": customers_count,
            "INACTIVE": inactive_count,
            "LOST": lost_count
        }
        
        avg_deal_value = (total_revenue / quotes_accepted) if quotes_accepted > 0 else 0.0
        total_pipeline = leads_count + prospects_count + customers_count
        conversion_rate = (customers_count / total_pipeline * 100) if total_pipeline > 0 else 0.0
        
        # Conversion funnel
        funnel_total = leads_count + prospects_count + customers_count + cold_leads_count
        conversion_funnel = [
            ConversionFunnelItem(
                status="Leads",
                count=leads_count,
                percentage=(leads_count / funnel_total * 100) if funnel_total > 0 else 0,
                color="#3498db"
            ),
            ConversionFunnelItem(
                status="Prospects",
                count=prospects_count,
                percentage=(prospects_count / funnel_total * 100) if funnel_total > 0 else 0,
                color="#9b59b6"
            ),
            ConversionFunnelItem(
                status="Customers",
                count=customers_count,
                percentage=(customers_count / funnel_total * 100) if funnel_total > 0 else 0,
                color="#2ecc71"
            ),
            ConversionFunnelItem(
                status="Cold/Inactive",
                count=cold_leads_count + inactive_count,
                percentage=((cold_leads_count + inactive_count) / funnel_total * 100) if funnel_total > 0 else 0,
                color="#95a5a6"
            )
        ]
        
        # AI insights (placeholder - can be enhanced later)
        ai_insights = []
        
        return DashboardResponse(
            stats=DashboardStats(
                total_discovery=discovery_count,
                total_leads=leads_count,
                total_prospects=prospects_count,
                total_opportunities=opportunities_count,
                total_customers=customers_count,
                total_cold_leads=cold_leads_count,
                total_inactive=inactive_count,
                total_quotes=total_quotes,
                quotes_pending=quotes_pending,
                quotes_accepted=quotes_accepted,
                total_revenue=total_revenue,
                avg_deal_value=avg_deal_value,
                conversion_rate=round(conversion_rate, 1),
                active_opportunities=active_opportunities,
                opportunities_qualified=opportunities_qualified,
                opportunities_proposal_sent=opportunities_proposal_sent,
                opportunities_closed_won=opportunities_closed_won,
                opportunities_total_value=opportunities_total_value,
                lifecycle_distribution=lifecycle_distribution,
                sla_compliance_rate=sla_compliance_rate,
                sla_active_breaches=sla_active_breaches,
                sla_tickets_at_risk=sla_tickets_at_risk,
                sla_total_tickets=sla_total_tickets
            ),
            conversion_funnel=conversion_funnel,
            pipeline_stages=pipeline_stages,
            recent_activity=recent_activity,
            monthly_trends=monthly_trends,
            ai_insights=ai_insights,
            top_leads=top_leads
        )
        
    except (Exception, DBAPIError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error: {e}", exc_info=True)
        try:
            await db.rollback()
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


class AIQueryRequest(BaseModel):
    query: str


class AIQueryResponse(BaseModel):
    response: str
    sources: List[str]


@router.post("/ai-query", response_model=AIQueryResponse)
async def ai_dashboard_query(
    request: AIQueryRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    AI-powered dashboard query system
    
    IMPORTANT: This endpoint provides comprehensive CRM context to the AI assistant.
    As we add more modules (quotes, campaigns, tasks, etc.), expand the context below
    to include relevant data from those modules.
    
    Current modules included:
    - Customers (all statuses)
    - Contacts
    - Monthly trends (last 6 months)
    - Top performing leads
    
    Future modules to add:
    - Quotes (pending, accepted, rejected)
    - Lead generation campaigns
    - Tasks and reminders
    - Customer interactions history
    - Financial analysis data
    """
    
    try:
        tenant_id = current_tenant.id
        
        # ===== API KEY RESOLUTION: Tenant keys first, then fall back to system keys =====
        # Get API keys using the centralized helper function
        # This checks tenant keys first, then falls back to system-wide keys from admin portal
        # Use sync session for get_api_keys (it expects sync session)
        from app.core.database import SessionLocal
        sync_db = SessionLocal()
        try:
            api_keys = get_api_keys(sync_db, current_tenant)
        finally:
            sync_db.close()
        
        # Initialize AI service with resolved API keys and tenant context
        # Use sync session for AI service (it may need sync operations)
        sync_db_for_ai = SessionLocal()
        try:
            ai_service = AIAnalysisService(
                openai_api_key=api_keys.openai,
                companies_house_api_key=api_keys.companies_house,
                google_maps_api_key=api_keys.google_maps,
                tenant_id=current_tenant.id,
                db=sync_db_for_ai
            )
        finally:
            sync_db_for_ai.close()
        
        # ===== CUSTOMER DATA =====
        total_customers_result = await db.execute(
            select(func.count(Customer.id)).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.is_deleted == False
                )
            )
        )
        total_customers = total_customers_result.scalar() or 0
        
        customers_by_status = {}
        for status in CustomerStatus:
            count_result = await db.execute(
                select(func.count(Customer.id)).where(
                    and_(
                        Customer.tenant_id == tenant_id,
                        Customer.status == status,
                        Customer.is_deleted == False
                    )
                )
            )
            customers_by_status[status.value] = count_result.scalar() or 0
        
        # ===== CONTACTS DATA =====
        total_contacts_result = await db.execute(
            select(func.count(Contact.id)).where(
                and_(
                    Contact.tenant_id == tenant_id,
                    Contact.is_deleted == False
                )
            )
        )
        total_contacts = total_contacts_result.scalar() or 0
        
        # ===== MONTHLY TRENDS (Last 6 months) =====
        now = datetime.utcnow()
        monthly_trends_data = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            new_leads_result = await db.execute(select(func.count(Lead.id)).where(
                and_(
                    Lead.tenant_id == tenant_id,
                    Lead.created_at >= month_start,
                    Lead.created_at <= month_end,
                    Lead.is_deleted == False
                )
            ))
            new_leads = new_leads_result.scalar() or 0
            
            converted_result = await db.execute(select(func.count(Customer.id)).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.status == CustomerStatus.CUSTOMER,
                    Customer.is_deleted == False,
                    Customer.created_at >= month_start,
                    Customer.created_at <= month_end
                )
            ))
            converted = converted_result.scalar() or 0
            
            monthly_trends_data.append({
                "month": calendar.month_abbr[month_start.month],
                "new_leads": new_leads,
                "converted": converted
            })
        
        # ===== TOP LEADS =====
        top_leads_result = await db.execute(
            select(Customer).where(
                and_(
                    Customer.tenant_id == tenant_id,
                    Customer.is_deleted == False,
                    Customer.status.in_([CustomerStatus.LEAD, CustomerStatus.PROSPECT, CustomerStatus.OPPORTUNITY]),
                    Customer.lead_score >= 70
                )
            ).order_by(Customer.lead_score.desc()).limit(10)
        )
        top_leads_data = top_leads_result.scalars().all()
        
        top_leads_list = []
        for lead in top_leads_data:
            top_leads_list.append({
                "company_name": lead.company_name,
                "status": lead.status.value if hasattr(lead.status, 'value') else str(lead.status),
                "lead_score": lead.lead_score or 0
            })
        
        # ===== BUILD CONTEXT FOR AI =====
        context = f"""
        CRM Dashboard Context for Tenant: {current_tenant.name}
        
        Total Customers: {total_customers}
        Customers by Status: {customers_by_status}
        Total Contacts: {total_contacts}
        
        Monthly Trends (Last 6 months):
        {monthly_trends_data}
        
        Top Performing Leads (Lead Score >= 70):
        {top_leads_list}
        
        User Query: {request.query}
        """
        
        # Use AI service to generate response
        # Note: This is a simplified version - you may want to use a more sophisticated prompt
        ai_response = await ai_service.analyze_company(
            company_name="Dashboard Query",
            company_number=None
        )
        
        return AIQueryResponse(
            response=ai_response.get("analysis", {}).get("summary", "Analysis completed"),
            sources=["CRM Database", "Monthly Trends", "Top Leads"]
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"AI dashboard query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing AI query: {str(e)}")
