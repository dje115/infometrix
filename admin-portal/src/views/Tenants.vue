<template>
  <div class="tenants">
    <div class="page-header">
      <h1>Tenant Management</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        Create New Tenant
      </el-button>
    </div>
    
    <!-- Info Banner -->
    <el-alert
      title="Module Access Control"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    >
      <template #default>
        <span>To enable/disable modules (Helpdesk, EnforceSense, Quoting, Sales) for a tenant, click the <strong>"Edit"</strong> button on any tenant row. The Module Access section will appear in the edit dialog.</span>
      </template>
    </el-alert>
    
    <!-- Filters -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filters.search"
            placeholder="Search tenants..."
            @input="loadTenants"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="Status" @change="loadTenants">
            <el-option label="All" value="" />
            <el-option label="Active" value="active" />
            <el-option label="Trial" value="trial" />
            <el-option label="Suspended" value="suspended" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- Tenants Table -->
    <el-card>
      <el-table :data="tenants" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="Name" />
        <el-table-column prop="company_name" label="Company" />
        <el-table-column prop="slug" label="Slug" />
        <el-table-column prop="domain" label="Domain" />
        <el-table-column prop="status" label="Status">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plan" label="Plan" />
        <el-table-column prop="created_at" label="Created" />
        <el-table-column label="Actions" width="250">
          <template #default="scope">
            <el-button size="small" type="primary" @click="editTenant(scope.row)">
              <el-icon><Edit /></el-icon>
              Edit
            </el-button>
            <el-button
              size="small"
              :type="scope.row.status === 'active' ? 'warning' : 'success'"
              @click="toggleTenantStatus(scope.row)"
            >
              {{ scope.row.status === 'active' ? 'Suspend' : 'Activate' }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteTenant(scope.row)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTenants"
          @current-change="loadTenants"
        />
      </div>
    </el-card>
    
    <!-- Create/Edit Tenant Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTenantId ? 'Edit Tenant' : 'Create New Tenant'"
      width="600px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="120px"
      >
        <el-form-item label="Name" prop="name">
          <el-input v-model="createForm.name" placeholder="Tenant name" />
        </el-form-item>
        
        <el-form-item label="Company Name" prop="company_name">
          <el-input v-model="createForm.company_name" placeholder="Legal company name (optional)" />
        </el-form-item>
        
        <el-form-item label="Slug" prop="slug">
          <el-input v-model="createForm.slug" placeholder="tenant-slug" />
        </el-form-item>
        
        <el-form-item label="Domain" prop="domain">
          <el-input v-model="createForm.domain" placeholder="tenant.example.com" />
        </el-form-item>
        
        <el-form-item label="Plan" prop="plan">
          <el-select v-model="createForm.plan" placeholder="Select plan">
            <el-option label="Trial" value="trial" />
            <el-option label="Basic" value="basic" />
            <el-option label="Professional" value="professional" />
            <el-option label="Enterprise" value="enterprise" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="!editingTenantId" label="Admin Email" prop="admin_email">
          <el-input v-model="createForm.admin_email" type="email" placeholder="admin@tenant.com" />
        </el-form-item>
        
        <el-form-item v-if="!editingTenantId" label="Admin Password" prop="admin_password">
          <el-input v-model="createForm.admin_password" type="password" placeholder="Password" />
        </el-form-item>
        
        <!-- Module Access Control -->
        <el-divider v-if="editingTenantId">
          <span style="font-weight: bold; font-size: 16px;">Module Access Control</span>
        </el-divider>
        <el-form-item v-if="editingTenantId" label="Enabled Modules" style="margin-top: 20px;">
          <el-card shadow="never" style="background-color: #f5f7fa; border: 1px solid #e4e7ed;">
            <el-checkbox-group v-model="createForm.feature_flags" style="display: flex; flex-direction: column; gap: 12px;">
              <el-checkbox label="HELPDESK_ENABLED" size="large">
                <span style="font-weight: 500;">Helpdesk</span>
                <span style="color: #909399; font-size: 12px; margin-left: 8px;">- Ticket management and SLA tracking</span>
              </el-checkbox>
              <el-checkbox label="ENFORCESENSE_ENABLED" size="large">
                <span style="font-weight: 500;">EnforceSense</span>
                <span style="color: #909399; font-size: 12px; margin-left: 8px;">- Debt enforcement and case management</span>
              </el-checkbox>
              <el-checkbox label="QUOTING_ENABLED" size="large">
                <span style="font-weight: 500;">Quoting</span>
                <span style="color: #909399; font-size: 12px; margin-left: 8px;">- Quote generation and proposals</span>
              </el-checkbox>
              <el-checkbox label="SALES_ENABLED" size="large">
                <span style="font-weight: 500;">Sales / CRM</span>
                <span style="color: #909399; font-size: 12px; margin-left: 8px;">- Customer relationship management</span>
              </el-checkbox>
            </el-checkbox-group>
            <div style="margin-top: 12px; padding: 8px; background-color: #e6f7ff; border-left: 3px solid #1890ff; border-radius: 4px;">
              <span style="color: #1890ff; font-size: 12px;">
                <i class="el-icon-info"></i> Select which modules this tenant has access to. Unchecked modules will be hidden from the tenant's navigation.
              </span>
            </div>
          </el-card>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="createTenant" :loading="creating">
          {{ editingTenantId ? 'Update Tenant' : 'Create Tenant' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

export default {
  name: 'Tenants',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const creating = ref(false)
    const showCreateDialog = ref(false)
    const editingTenantId = ref(null)
    const tenants = ref([])
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    
    const filters = reactive({
      search: '',
      status: ''
    })
    
    const createForm = reactive({
      name: '',
      company_name: '',
      slug: '',
      domain: '',
      plan: 'trial',
      admin_email: '',
      admin_password: '',
      feature_flags: []  // Array of enabled feature flag names
    })
    
    const createRules = {
      name: [{ required: true, message: 'Please enter tenant name', trigger: 'blur' }],
      slug: [{ required: true, message: 'Please enter tenant slug', trigger: 'blur' }],
      admin_email: [{ required: true, message: 'Please enter admin email', trigger: 'blur' }],
      admin_password: [{ required: true, message: 'Please enter admin password', trigger: 'blur' }]
    }
    
    const getStatusType = (status) => {
      switch (status) {
        case 'active': return 'success'
        case 'trial': return 'warning'
        case 'suspended': return 'danger'
        default: return 'info'
      }
    }
    
    const loadTenants = async () => {
      loading.value = true
      try {
        const token = localStorage.getItem('admin_token')
        
        const params = {
          page: currentPage.value,
          size: pageSize.value,
          search: filters.search,
          status: filters.status
        }
        
        const response = await axios.get('http://localhost:8000/api/v1/admin/tenants', { 
          params,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        tenants.value = response.data.tenants
        total.value = response.data.total
      } catch (error) {
        console.error('Failed to load tenants:', error)
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('admin_token')
          router.push('/login')
        } else {
          ElMessage.error('Failed to load tenants')
        }
      } finally {
        loading.value = false
      }
    }
    
    const createTenant = async () => {
      try {
        creating.value = true
        const token = localStorage.getItem('admin_token')
        
        if (editingTenantId.value) {
          // Update existing tenant
          // Convert feature flags array to object format
          const updateData = {
            name: createForm.name,
            company_name: createForm.company_name,
            slug: createForm.slug,
            domain: createForm.domain,
            plan: createForm.plan,
            feature_flags: {},
            enabled_modules: []
          }
          
          // Build feature flags object from checked items
          const allFlags = ['HELPDESK_ENABLED', 'ENFORCESENSE_ENABLED', 'QUOTING_ENABLED', 'SALES_ENABLED']
          allFlags.forEach(flag => {
            updateData.feature_flags[flag] = createForm.feature_flags.includes(flag)
          })
          
          // Map feature flags to module IDs for enabled_modules
          // CRM is always enabled
          updateData.enabled_modules.push('crm')
          
          // Map feature flags to modules
          if (createForm.feature_flags.includes('HELPDESK_ENABLED')) {
            updateData.enabled_modules.push('helpdesk')
          }
          if (createForm.feature_flags.includes('ENFORCESENSE_ENABLED')) {
            updateData.enabled_modules.push('enforcesense')
          }
          if (createForm.feature_flags.includes('QUOTING_ENABLED')) {
            updateData.enabled_modules.push('quoting')
          }
          // SALES_ENABLED is part of CRM, so no separate module
          
          await axios.put(`http://localhost:8000/api/v1/admin/tenants/${editingTenantId.value}`, updateData, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          ElMessage.success('Tenant updated successfully!')
        } else {
          // Create new tenant
          await axios.post('http://localhost:8000/api/v1/admin/tenants', createForm, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          ElMessage.success('Tenant created successfully!')
        }
        
        showCreateDialog.value = false
        editingTenantId.value = null
        loadTenants()
        
        // Reset form
        Object.assign(createForm, {
          name: '',
          company_name: '',
          slug: '',
          domain: '',
          plan: 'trial',
          admin_email: '',
          admin_password: '',
          feature_flags: []
        })
      } catch (error) {
        console.error('Failed to save tenant:', error)
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token')
          router.push('/login')
        } else {
          ElMessage.error(error.response?.data?.detail || 'Failed to save tenant')
        }
      } finally {
        creating.value = false
      }
    }
    
    const editTenant = async (tenant) => {
      try {
        loading.value = true
        const token = localStorage.getItem('admin_token')
        
        // Fetch full tenant details including feature flags
        const response = await axios.get(`http://localhost:8000/api/v1/admin/tenants/${tenant.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        const tenantData = response.data
        
        // Convert feature flags object to array of enabled flags
        const enabledFlags = []
        if (tenantData.feature_flags) {
          Object.keys(tenantData.feature_flags).forEach(flag => {
            if (tenantData.feature_flags[flag] === true) {
              enabledFlags.push(flag)
            }
          })
        }
        
        // If enabled_modules exists, use it to determine feature flags
        // Otherwise, derive from feature_flags
        let enabledFlagsToUse = enabledFlags
        if (tenantData.enabled_modules && tenantData.enabled_modules.length > 0) {
          // Map enabled_modules to feature flags
          enabledFlagsToUse = []
          if (tenantData.enabled_modules.includes('helpdesk')) {
            enabledFlagsToUse.push('HELPDESK_ENABLED')
          }
          if (tenantData.enabled_modules.includes('enforcesense')) {
            enabledFlagsToUse.push('ENFORCESENSE_ENABLED')
          }
          if (tenantData.enabled_modules.includes('quoting')) {
            enabledFlagsToUse.push('QUOTING_ENABLED')
          }
          // CRM is always enabled, so SALES_ENABLED should be checked if CRM is in enabled_modules
          if (tenantData.enabled_modules.includes('crm')) {
            enabledFlagsToUse.push('SALES_ENABLED')
          }
        }
        
        // Pre-fill the create form with existing tenant data
        Object.assign(createForm, {
          name: tenantData.name,
          company_name: tenantData.company_name || '',
          slug: tenantData.slug,
          domain: tenantData.domain || '',
          plan: tenantData.plan,
          admin_email: '', // Don't show current admin email for security
          admin_password: '', // Don't show current password for security
          feature_flags: enabledFlagsToUse
        })
        
        // Store the tenant ID for update
        editingTenantId.value = tenant.id
        showCreateDialog.value = true
      } catch (error) {
        console.error('Failed to load tenant details:', error)
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token')
          router.push('/login')
        } else {
          ElMessage.error('Failed to load tenant details')
        }
      } finally {
        loading.value = false
      }
    }
    
    const toggleTenantStatus = async (tenant) => {
      try {
        const token = localStorage.getItem('admin_token')
        let newStatus, action
        
        if (tenant.status === 'active') {
          newStatus = 'suspended'
          action = 'suspended'
        } else if (tenant.status === 'trial') {
          newStatus = 'active'
          action = 'activated'
        } else {
          newStatus = 'active'
          action = 'activated'
        }
        
        await axios.patch(`http://localhost:8000/api/v1/admin/tenants/${tenant.id}/status`, {
          status: newStatus
        }, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        ElMessage.success(`Tenant ${action} successfully!`)
        loadTenants()
      } catch (error) {
        console.error('Failed to update tenant status:', error)
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token')
          router.push('/login')
        } else {
          ElMessage.error('Failed to update tenant status')
        }
      }
    }
    
    const deleteTenant = async (tenant) => {
      try {
        await ElMessageBox.confirm(
          `Are you sure you want to delete tenant "${tenant.name}"? This action cannot be undone.`,
          'Confirm Delete',
          {
            confirmButtonText: 'Delete',
            cancelButtonText: 'Cancel',
            type: 'warning'
          }
        )
        
        const token = localStorage.getItem('admin_token')
        await axios.delete(`http://localhost:8000/api/v1/admin/tenants/${tenant.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        ElMessage.success('Tenant deleted successfully!')
        loadTenants()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete tenant:', error)
          if (error.response?.status === 401) {
            localStorage.removeItem('admin_token')
            router.push('/login')
          } else {
            ElMessage.error('Failed to delete tenant')
          }
        }
      }
    }
    
    onMounted(() => {
      loadTenants()
    })
    
    return {
      loading,
      creating,
      showCreateDialog,
      editingTenantId,
      tenants,
      currentPage,
      pageSize,
      total,
      filters,
      createForm,
      createRules,
      getStatusType,
      loadTenants,
      createTenant,
      editTenant,
      toggleTenantStatus,
      deleteTenant
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style>
