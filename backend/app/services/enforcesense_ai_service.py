#!/usr/bin/env python3
"""
EnforceSense AI Service

Handles AI-powered note improvement and case analysis
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.enforcesense import CaseNote, EnforcementCase, Debtor
from app.services.ai_provider_service import AIProviderService
from app.models.ai_prompt import PromptCategory

logger = logging.getLogger(__name__)


class EnforceSenseAIService:
    """Service for AI-powered EnforceSense features"""
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.provider_service = AIProviderService(db, tenant_id=tenant_id)
    
    async def improve_note(self, note_id: str) -> Dict[str, Any]:
        """
        Improve a case note using AI
        
        CRITICAL: Original note is never overwritten.
        AI generates cleaned/improved version.
        """
        try:
            # Get note
            stmt = select(CaseNote).where(
                and_(
                    CaseNote.id == note_id,
                    CaseNote.tenant_id == self.tenant_id,
                    CaseNote.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            note = result.scalar_one_or_none()
            
            if not note:
                raise ValueError(f"Note {note_id} not found")
            
            # Update status to processing
            note.ai_processing_status = 'processing'
            await self.db.commit()
            
            # Get case context
            case_stmt = select(EnforcementCase).where(EnforcementCase.id == note.case_id)
            case_result = await self.db.execute(case_stmt)
            case = case_result.scalar_one_or_none()
            
            debtor_context = ""
            if case:
                debtor_stmt = select(Debtor).where(Debtor.id == case.debtor_id)
                debtor_result = await self.db.execute(debtor_stmt)
                debtor = debtor_result.scalar_one_or_none()
                if debtor:
                    debtor_context = f"Debtor: {debtor.legal_name} ({debtor.entity_type})"
            
            # Build AI prompt
            prompt = f"""You are an AI assistant helping enforcement agents write professional, clear, and compliant case notes.

Original Note:
{note.original_note or note.note}

Context:
{debtor_context}
Case Type: {case.case_type.value if case else 'Unknown'}

Your task:
1. Clean up the note for clarity and professionalism
2. Remove emotional language, maintain neutral tone
3. Structure the note logically
4. Identify any risk flags (inappropriate language, compliance issues, etc.)
5. Generate a brief summary

Return JSON format:
{{
    "cleaned_note": "Professional, clear version of the note",
    "summary": "Brief summary of the note content",
    "risk_flags": ["flag1", "flag2"] or [],
    "tone_issues": ["issue1"] or []
}}"""
            
            # Call AI service
            response = await self.provider_service.generate(
                prompt=prompt,
                system_prompt="You are a professional enforcement case management assistant. Always return valid JSON.",
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            import json
            ai_result = json.loads(response.content)
            
            # Update note with AI improvements
            note.ai_improved_note = ai_result.get('cleaned_note', '')
            note.ai_summary = ai_result.get('summary', '')
            note.risk_flags = ai_result.get('risk_flags', [])
            
            # Update the main note field to show improved version
            if note.ai_improved_note:
                note.note = note.ai_improved_note
            
            note.ai_processing_status = 'completed'
            
            await self.db.commit()
            await self.db.refresh(note)
            
            logger.info(f"Successfully improved note {note_id}")
            
            return {
                "success": True,
                "note_id": note_id,
                "improved_note": note.ai_improved_note,
                "summary": note.ai_summary,
                "risk_flags": note.risk_flags
            }
            
        except Exception as e:
            logger.error(f"Error improving note {note_id}: {e}", exc_info=True)
            
            # Update status to failed
            try:
                note_stmt = select(CaseNote).where(CaseNote.id == note_id)
                note_result = await self.db.execute(note_stmt)
                note = note_result.scalar_one_or_none()
                if note:
                    note.ai_processing_status = 'failed'
                    await self.db.commit()
            except:
                pass
            
            return {
                "success": False,
                "error": str(e)
            }



