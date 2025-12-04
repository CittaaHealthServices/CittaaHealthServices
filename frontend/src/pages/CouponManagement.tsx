import { useState, useEffect } from 'react'
import { couponService, Coupon } from '../services/api'
import { 
  Ticket, Plus, Edit2, Trash2, ToggleLeft, ToggleRight,
  Percent, DollarSign, Clock, Copy, Check, X, Search
} from 'lucide-react'

export default function CouponManagement() {
  const [coupons, setCoupons] = useState<Coupon[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingCoupon, setEditingCoupon] = useState<Coupon | null>(null)
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')

  // Form state
  const [formData, setFormData] = useState({
    code: '',
    discount_type: 'percentage' as 'percentage' | 'fixed_amount' | 'free_trial',
    discount_value: 0,
    description: '',
    max_uses: undefined as number | undefined,
    valid_from: new Date().toISOString().split('T')[0],
    valid_until: '',
    applicable_plans: [] as string[]
  })

  useEffect(() => {
    loadCoupons()
  }, [])

  const loadCoupons = async () => {
    try {
      setLoading(true)
      const data = await couponService.getAllCoupons()
      setCoupons(data.coupons || data || [])
    } catch (err) {
      setError('Failed to load coupons')
      console.error(err)
      // Set empty array for demo if API not available
      setCoupons([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCoupon = async () => {
    try {
      await couponService.createCoupon({
        ...formData,
        max_uses: formData.max_uses || undefined,
        valid_until: formData.valid_until || undefined
      })
      setShowCreateModal(false)
      resetForm()
      loadCoupons()
    } catch (err) {
      setError('Failed to create coupon')
      console.error(err)
    }
  }

  const handleUpdateCoupon = async () => {
    if (!editingCoupon) return
    try {
      await couponService.updateCoupon(editingCoupon.id, formData)
      setEditingCoupon(null)
      resetForm()
      loadCoupons()
    } catch (err) {
      setError('Failed to update coupon')
      console.error(err)
    }
  }

  const handleDeleteCoupon = async (couponId: string) => {
    if (!confirm('Are you sure you want to delete this coupon?')) return
    try {
      await couponService.deleteCoupon(couponId)
      loadCoupons()
    } catch (err) {
      setError('Failed to delete coupon')
      console.error(err)
    }
  }

  const handleToggleStatus = async (couponId: string) => {
    try {
      await couponService.toggleCouponStatus(couponId)
      loadCoupons()
    } catch (err) {
      setError('Failed to toggle coupon status')
      console.error(err)
    }
  }

  const resetForm = () => {
    setFormData({
      code: '',
      discount_type: 'percentage',
      discount_value: 0,
      description: '',
      max_uses: undefined,
      valid_from: new Date().toISOString().split('T')[0],
      valid_until: '',
      applicable_plans: []
    })
  }

  const openEditModal = (coupon: Coupon) => {
    setEditingCoupon(coupon)
    setFormData({
      code: coupon.code,
      discount_type: coupon.discount_type,
      discount_value: coupon.discount_value,
      description: coupon.description || '',
      max_uses: coupon.max_uses,
      valid_from: coupon.valid_from.split('T')[0],
      valid_until: coupon.valid_until?.split('T')[0] || '',
      applicable_plans: coupon.applicable_plans || []
    })
  }

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const generateRandomCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    let code = 'CITTAA'
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    setFormData({ ...formData, code })
  }

  const getDiscountDisplay = (coupon: Coupon) => {
    switch (coupon.discount_type) {
      case 'percentage':
        return `${coupon.discount_value}% OFF`
      case 'fixed_amount':
        return `₹${coupon.discount_value} OFF`
      case 'free_trial':
        return `${coupon.discount_value} Days Free`
      default:
        return coupon.discount_value.toString()
    }
  }

  const getDiscountIcon = (type: string) => {
    switch (type) {
      case 'percentage':
        return <Percent className="w-4 h-4" />
      case 'fixed_amount':
        return <DollarSign className="w-4 h-4" />
      case 'free_trial':
        return <Clock className="w-4 h-4" />
      default:
        return <Ticket className="w-4 h-4" />
    }
  }

  const filteredCoupons = coupons.filter(coupon => {
    const matchesSearch = coupon.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      coupon.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterType === 'all' || coupon.discount_type === filterType
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Ticket className="w-12 h-12 text-primary-500 animate-bounce" />
          <p className="mt-4 text-gray-500">Loading coupons...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-accent-400 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Ticket className="w-7 h-7" />
              Coupon Management
            </h1>
            <p className="mt-1 text-white/80">
              Create and manage discount coupons for premium subscriptions
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium flex items-center gap-2 hover:bg-white/90 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Create Coupon
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search coupons..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="percentage">Percentage</option>
            <option value="fixed_amount">Fixed Amount</option>
            <option value="free_trial">Free Trial</option>
          </select>
        </div>
      </div>

      {/* Coupons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCoupons.length === 0 ? (
          <div className="col-span-full bg-white rounded-xl p-12 text-center shadow-sm border border-gray-100">
            <Ticket className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600">No coupons found</h3>
            <p className="text-gray-400 mt-1">Create your first coupon to get started</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 bg-primary-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-primary-600 transition-colors"
            >
              Create Coupon
            </button>
          </div>
        ) : (
          filteredCoupons.map((coupon) => (
            <div
              key={coupon.id}
              className={`bg-white rounded-xl p-5 shadow-sm border-2 transition-all duration-200 ${
                coupon.is_active ? 'border-primary-200 hover:border-primary-400' : 'border-gray-200 opacity-60'
              }`}
            >
              {/* Coupon Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg ${
                    coupon.discount_type === 'percentage' ? 'bg-primary-100 text-primary-600' :
                    coupon.discount_type === 'fixed_amount' ? 'bg-accent-100 text-accent-600' :
                    'bg-secondary-100 text-secondary-600'
                  }`}>
                    {getDiscountIcon(coupon.discount_type)}
                  </div>
                  <div>
                    <p className="font-bold text-lg text-gray-800">{getDiscountDisplay(coupon)}</p>
                    <p className="text-xs text-gray-500 capitalize">{coupon.discount_type.replace('_', ' ')}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleToggleStatus(coupon.id)}
                  className={`p-1 rounded-full transition-colors ${
                    coupon.is_active ? 'text-success hover:bg-success/10' : 'text-gray-400 hover:bg-gray-100'
                  }`}
                >
                  {coupon.is_active ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6" />}
                </button>
              </div>

              {/* Coupon Code */}
              <div className="bg-gray-50 rounded-lg p-3 mb-3 flex items-center justify-between">
                <code className="font-mono font-bold text-primary-600 tracking-wider">{coupon.code}</code>
                <button
                  onClick={() => copyToClipboard(coupon.code)}
                  className="p-1.5 hover:bg-gray-200 rounded-md transition-colors"
                >
                  {copiedCode === coupon.code ? (
                    <Check className="w-4 h-4 text-success" />
                  ) : (
                    <Copy className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              </div>

              {/* Description */}
              {coupon.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{coupon.description}</p>
              )}

              {/* Stats */}
              <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                <span>Used: {coupon.current_uses}{coupon.max_uses ? `/${coupon.max_uses}` : ''}</span>
                {coupon.valid_until && (
                  <span>Expires: {new Date(coupon.valid_until).toLocaleDateString()}</span>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                <button
                  onClick={() => openEditModal(coupon)}
                  className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteCoupon(coupon.id)}
                  className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingCoupon) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-800">
                  {editingCoupon ? 'Edit Coupon' : 'Create New Coupon'}
                </h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingCoupon(null)
                    resetForm()
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              {/* Coupon Code */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Coupon Code</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                    placeholder="CITTAA2024"
                    className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono uppercase"
                  />
                  <button
                    type="button"
                    onClick={generateRandomCode}
                    className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Generate
                  </button>
                </div>
              </div>

              {/* Discount Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Discount Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'percentage', label: 'Percentage', icon: Percent },
                    { value: 'fixed_amount', label: 'Fixed Amount', icon: DollarSign },
                    { value: 'free_trial', label: 'Free Trial', icon: Clock }
                  ].map(({ value, label, icon: Icon }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setFormData({ ...formData, discount_type: value as typeof formData.discount_type })}
                      className={`p-3 rounded-lg border-2 flex flex-col items-center gap-1 transition-all ${
                        formData.discount_type === value
                          ? 'border-primary-500 bg-primary-50 text-primary-600'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-xs font-medium">{label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Discount Value */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {formData.discount_type === 'percentage' ? 'Discount Percentage' :
                   formData.discount_type === 'fixed_amount' ? 'Discount Amount (₹)' :
                   'Free Trial Days'}
                </label>
                <input
                  type="number"
                  value={formData.discount_value}
                  onChange={(e) => setFormData({ ...formData, discount_value: Number(e.target.value) })}
                  placeholder={formData.discount_type === 'percentage' ? '50' : formData.discount_type === 'fixed_amount' ? '500' : '30'}
                  min="0"
                  max={formData.discount_type === 'percentage' ? 100 : undefined}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Special discount for early adopters..."
                  rows={2}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                />
              </div>

              {/* Max Uses */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Uses (Optional)</label>
                <input
                  type="number"
                  value={formData.max_uses || ''}
                  onChange={(e) => setFormData({ ...formData, max_uses: e.target.value ? Number(e.target.value) : undefined })}
                  placeholder="Unlimited"
                  min="1"
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Validity Period */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valid From</label>
                  <input
                    type="date"
                    value={formData.valid_from}
                    onChange={(e) => setFormData({ ...formData, valid_from: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valid Until (Optional)</label>
                  <input
                    type="date"
                    value={formData.valid_until}
                    onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setEditingCoupon(null)
                  resetForm()
                }}
                className="flex-1 px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={editingCoupon ? handleUpdateCoupon : handleCreateCoupon}
                className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium"
              >
                {editingCoupon ? 'Update Coupon' : 'Create Coupon'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
