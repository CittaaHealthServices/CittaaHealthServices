import { useState } from 'react'
import { 
  Search, 
  Plus, 
  Ticket,
  Copy,
  Trash2,
  Edit,
  CheckCircle,
  XCircle,
  Percent,
  IndianRupee,
  Gift,
  Calendar
} from 'lucide-react'

interface Coupon {
  id: string
  code: string
  description: string
  discountType: 'PERCENT' | 'AMOUNT' | 'FREE_TRIAL'
  discountValue: number
  maxRedemptions: number
  currentRedemptions: number
  applicablePlans: string[]
  validFrom: string
  validUntil: string
  status: 'active' | 'inactive' | 'expired'
  createdAt: string
}

const mockCoupons: Coupon[] = [
  { id: 'C001', code: 'CITTAA50', description: '50% off first month', discountType: 'PERCENT', discountValue: 50, maxRedemptions: 100, currentRedemptions: 45, applicablePlans: ['PREMIUM_INDIVIDUAL', 'PREMIUM_PLUS'], validFrom: '2024-01-01', validUntil: '2024-03-31', status: 'active', createdAt: '2024-01-01' },
  { id: 'C002', code: 'WELCOME500', description: '₹500 off any plan', discountType: 'AMOUNT', discountValue: 500, maxRedemptions: 200, currentRedemptions: 123, applicablePlans: ['PREMIUM_INDIVIDUAL', 'PREMIUM_PLUS', 'CORPORATE'], validFrom: '2024-01-01', validUntil: '2024-06-30', status: 'active', createdAt: '2024-01-01' },
  { id: 'C003', code: 'FREETRIAL30', description: '30 days free trial', discountType: 'FREE_TRIAL', discountValue: 30, maxRedemptions: 50, currentRedemptions: 50, applicablePlans: ['PREMIUM_INDIVIDUAL'], validFrom: '2024-01-01', validUntil: '2024-02-28', status: 'expired', createdAt: '2024-01-01' },
  { id: 'C004', code: 'CORPORATE25', description: '25% off corporate plans', discountType: 'PERCENT', discountValue: 25, maxRedemptions: 20, currentRedemptions: 8, applicablePlans: ['CORPORATE'], validFrom: '2024-02-01', validUntil: '2024-12-31', status: 'active', createdAt: '2024-02-01' },
  { id: 'C005', code: 'LAUNCH1000', description: '₹1000 launch discount', discountType: 'AMOUNT', discountValue: 1000, maxRedemptions: 100, currentRedemptions: 0, applicablePlans: ['PREMIUM_PLUS'], validFrom: '2024-03-01', validUntil: '2024-03-31', status: 'inactive', createdAt: '2024-02-15' },
]

export function CouponManagement() {
  const [coupons, setCoupons] = useState(mockCoupons)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_editingCoupon, setEditingCoupon] = useState<Coupon | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    code: '',
    description: '',
    discountType: 'PERCENT' as 'PERCENT' | 'AMOUNT' | 'FREE_TRIAL',
    discountValue: 0,
    maxRedemptions: 100,
    applicablePlans: ['PREMIUM_INDIVIDUAL'],
    validFrom: '',
    validUntil: ''
  })

  const filteredCoupons = coupons.filter(coupon =>
    coupon.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    coupon.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const handleCreateCoupon = () => {
    const newCoupon: Coupon = {
      id: `C${String(coupons.length + 1).padStart(3, '0')}`,
      ...formData,
      currentRedemptions: 0,
      status: 'active',
      createdAt: new Date().toISOString().split('T')[0]
    }
    setCoupons([...coupons, newCoupon])
    setShowCreateModal(false)
    resetForm()
  }

  const handleToggleStatus = (couponId: string) => {
    setCoupons(coupons.map(c => 
      c.id === couponId 
        ? { ...c, status: c.status === 'active' ? 'inactive' : 'active' as const }
        : c
    ))
  }

  const handleDeleteCoupon = (couponId: string) => {
    setCoupons(coupons.filter(c => c.id !== couponId))
  }

  const resetForm = () => {
    setFormData({
      code: '',
      description: '',
      discountType: 'PERCENT',
      discountValue: 0,
      maxRedemptions: 100,
      applicablePlans: ['PREMIUM_INDIVIDUAL'],
      validFrom: '',
      validUntil: ''
    })
  }

  const getDiscountIcon = (type: string) => {
    switch (type) {
      case 'PERCENT': return <Percent className="w-4 h-4" />
      case 'AMOUNT': return <IndianRupee className="w-4 h-4" />
      case 'FREE_TRIAL': return <Gift className="w-4 h-4" />
      default: return <Ticket className="w-4 h-4" />
    }
  }

  const getDiscountDisplay = (coupon: Coupon) => {
    switch (coupon.discountType) {
      case 'PERCENT': return `${coupon.discountValue}% off`
      case 'AMOUNT': return `₹${coupon.discountValue} off`
      case 'FREE_TRIAL': return `${coupon.discountValue} days free`
      default: return ''
    }
  }

  const activeCoupons = coupons.filter(c => c.status === 'active').length
  const totalRedemptions = coupons.reduce((sum, c) => sum + c.currentRedemptions, 0)

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Coupon Management</h1>
          <p className="text-gray-600 mt-1">Create and manage promotional coupons</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Coupon
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <Ticket className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Coupons</p>
              <p className="text-2xl font-bold text-gray-900">{coupons.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Coupons</p>
              <p className="text-2xl font-bold text-gray-900">{activeCoupons}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Gift className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Redemptions</p>
              <p className="text-2xl font-bold text-gray-900">{totalRedemptions}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-orange-100 rounded-lg">
              <IndianRupee className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Est. Savings</p>
              <p className="text-2xl font-bold text-gray-900">₹1.2L</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search coupons..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>
      </div>

      {/* Coupons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCoupons.map((coupon) => (
          <div key={coupon.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden card-hover">
            {/* Coupon Header */}
            <div className={`p-4 ${
              coupon.status === 'active' ? 'bg-green-50' :
              coupon.status === 'expired' ? 'bg-gray-50' :
              'bg-yellow-50'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  coupon.status === 'active' ? 'bg-green-100 text-green-700' :
                  coupon.status === 'expired' ? 'bg-gray-200 text-gray-600' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {coupon.status.charAt(0).toUpperCase() + coupon.status.slice(1)}
                </span>
                <div className="flex items-center gap-1">
                  {getDiscountIcon(coupon.discountType)}
                  <span className="text-sm font-medium">{getDiscountDisplay(coupon)}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <code className="text-lg font-bold text-gray-900 bg-white px-3 py-1 rounded border-2 border-dashed border-gray-300">
                  {coupon.code}
                </code>
                <button
                  onClick={() => handleCopyCode(coupon.code)}
                  className="p-2 hover:bg-white rounded-lg transition-colors"
                  title="Copy code"
                >
                  {copiedCode === coupon.code ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* Coupon Body */}
            <div className="p-4">
              <p className="text-sm text-gray-600 mb-3">{coupon.description}</p>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500">Redemptions</span>
                  <span className="font-medium">{coupon.currentRedemptions}/{coupon.maxRedemptions}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    className="bg-green-500 h-1.5 rounded-full"
                    style={{ width: `${(coupon.currentRedemptions / coupon.maxRedemptions) * 100}%` }}
                  />
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Calendar className="w-3 h-3" />
                  <span className="text-xs">{coupon.validFrom} - {coupon.validUntil}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mt-3">
                {coupon.applicablePlans.map((plan) => (
                  <span key={plan} className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">
                    {plan.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>

            {/* Coupon Actions */}
            <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
              <button
                onClick={() => handleToggleStatus(coupon.id)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  coupon.status === 'active'
                    ? 'text-yellow-600 hover:bg-yellow-50'
                    : 'text-green-600 hover:bg-green-50'
                }`}
              >
                {coupon.status === 'active' ? (
                  <>
                    <XCircle className="w-4 h-4" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Activate
                  </>
                )}
              </button>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setEditingCoupon(coupon)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDeleteCoupon(coupon.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Coupon Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-lg mx-4 animate-slide-in max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Create New Coupon</h2>
              <p className="text-gray-500 mt-1">Set up a promotional coupon for your users</p>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Coupon Code</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="e.g., CITTAA50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="e.g., 50% off first month"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Discount Type</label>
                  <select
                    value={formData.discountType}
                    onChange={(e) => setFormData({ ...formData, discountType: e.target.value as any })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  >
                    <option value="PERCENT">Percentage</option>
                    <option value="AMOUNT">Fixed Amount</option>
                    <option value="FREE_TRIAL">Free Trial</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {formData.discountType === 'PERCENT' ? 'Percentage' : 
                     formData.discountType === 'AMOUNT' ? 'Amount (₹)' : 'Days'}
                  </label>
                  <input
                    type="number"
                    value={formData.discountValue}
                    onChange={(e) => setFormData({ ...formData, discountValue: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Redemptions</label>
                <input
                  type="number"
                  value={formData.maxRedemptions}
                  onChange={(e) => setFormData({ ...formData, maxRedemptions: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valid From</label>
                  <input
                    type="date"
                    value={formData.validFrom}
                    onChange={(e) => setFormData({ ...formData, validFrom: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valid Until</label>
                  <input
                    type="date"
                    value={formData.validUntil}
                    onChange={(e) => setFormData({ ...formData, validUntil: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Applicable Plans</label>
                <div className="flex flex-wrap gap-2">
                  {['PREMIUM_INDIVIDUAL', 'PREMIUM_PLUS', 'CORPORATE'].map((plan) => (
                    <label key={plan} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.applicablePlans.includes(plan)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({ ...formData, applicablePlans: [...formData.applicablePlans, plan] })
                          } else {
                            setFormData({ ...formData, applicablePlans: formData.applicablePlans.filter(p => p !== plan) })
                          }
                        }}
                        className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <span className="text-sm text-gray-700">{plan.replace('_', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  resetForm()
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCoupon}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Create Coupon
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
