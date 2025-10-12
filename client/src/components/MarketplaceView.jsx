import { useState, useEffect } from 'react'
import './MarketplaceView.css'

const MARKETPLACE_URL = 'http://localhost:9999'

function MarketplaceView({ onInstall }) {
  const [packages, setPackages] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedPackage, setSelectedPackage] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // grid | list

  useEffect(() => {
    loadCategories()
    loadPackages()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await fetch(`${MARKETPLACE_URL}/marketplace/categories`)
      const data = await response.json()
      setCategories(data.categories)
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  const loadPackages = async (query = '', category = null) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (query) params.append('query', query)
      if (category) params.append('category', category)
      
      const response = await fetch(`${MARKETPLACE_URL}/marketplace/packages?${params}`)
      const data = await response.json()
      setPackages(data.packages || [])
    } catch (error) {
      console.error('加载包失败:', error)
      setPackages([])
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (query) => {
    setSearchQuery(query)
    loadPackages(query, selectedCategory)
  }

  const handleCategoryClick = (categoryId) => {
    setSelectedCategory(categoryId)
    loadPackages(searchQuery, categoryId)
  }

  const handlePackageClick = async (pkg) => {
    try {
      const response = await fetch(`${MARKETPLACE_URL}/marketplace/packages/${pkg.id}`)
      const data = await response.json()
      setSelectedPackage(data)
    } catch (error) {
      console.error('加载包详情失败:', error)
    }
  }

  const handleInstall = async (pkg) => {
    if (!confirm(`确定要安装 "${pkg.name}" v${pkg.version} 吗？`)) return

    try {
      const downloadResponse = await fetch(
        `${MARKETPLACE_URL}/marketplace/packages/${pkg.id}/download`,
        { method: 'POST' }
      )
      
      if (!downloadResponse.ok) {
        throw new Error('下载失败')
      }
      
      const downloadData = await downloadResponse.json()

      const installResponse = await fetch('/api/servers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: pkg.id.replace('/', '-'),
          type: downloadData.type,
          ...downloadData.install_config
        })
      })

      if (installResponse.ok) {
        alert(`✅ ${pkg.name} v${pkg.version} 安装成功！\n\n请前往"MCP 服务器"页面连接使用。`)
        onInstall && onInstall()
        setSelectedPackage(null)
      } else {
        const errorData = await installResponse.json()
        throw new Error(errorData.detail || '安装失败')
      }
    } catch (error) {
      alert(`❌ 安装失败: ${error.message}`)
      console.error('安装错误:', error)
    }
  }

  const closeModal = () => {
    setSelectedPackage(null)
  }

  return (
    <div className="marketplace">
      {/* 顶部导航栏 */}
      <div className="marketplace-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="marketplace-title">
              <span className="title-icon">🏪</span>
              Marketplace
            </h1>
            <div className="header-stats">
              <span className="stat-item">
                <span className="stat-number">{packages.length}</span>
                <span className="stat-label">Packages</span>
              </span>
              <span className="stat-item">
                <span className="stat-number">{categories.length}</span>
                <span className="stat-label">Categories</span>
              </span>
            </div>
          </div>
          
          <div className="header-right">
            <div className="view-controls">
              <button 
                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode('grid')}
                title="网格视图"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
              </button>
              <button 
                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode('list')}
                title="列表视图"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <line x1="8" y1="6" x2="21" y2="6"/>
                  <line x1="8" y1="12" x2="21" y2="12"/>
                  <line x1="8" y1="18" x2="21" y2="18"/>
                  <line x1="3" y1="6" x2="3.01" y2="6"/>
                  <line x1="3" y1="12" x2="3.01" y2="12"/>
                  <line x1="3" y1="18" x2="3.01" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* 搜索栏 */}
        <div className="search-section">
          <div className="search-container">
            <div className="search-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <input
              type="text"
              placeholder="搜索 MCP Servers..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button 
                className="search-clear"
                onClick={() => handleSearch('')}
                title="清除搜索"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 分类筛选器 */}
      <div className="filter-section">
        <div className="filter-content">
          <div className="filter-tabs">
            <button
              className={`filter-tab ${!selectedCategory ? 'active' : ''}`}
              onClick={() => handleCategoryClick(null)}
            >
              <span className="tab-icon">📦</span>
              <span className="tab-label">全部</span>
              <span className="tab-count">{packages.length}</span>
            </button>
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`filter-tab ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => handleCategoryClick(cat.id)}
              >
                <span className="tab-icon">{cat.icon}</span>
                <span className="tab-label">{cat.name}</span>
                <span className="tab-count">{cat.count}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="marketplace-content">
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner">
              <div className="spinner-ring"></div>
            </div>
            <p className="loading-text">正在加载...</p>
          </div>
        ) : packages.length === 0 ? (
          <div className="empty-container">
            <div className="empty-icon">🔍</div>
            <h3 className="empty-title">未找到相关包</h3>
            <p className="empty-description">尝试调整搜索条件或选择其他分类</p>
          </div>
        ) : (
          <div className={`packages-container ${viewMode}`}>
            {packages.map(pkg => (
              <div 
                key={pkg.id} 
                className={`package-item ${viewMode}`}
                onClick={() => handlePackageClick(pkg)}
              >
                <div className="package-header">
                  <div className="package-icon">
                    {pkg.icon_url ? (
                      <img src={pkg.icon_url} alt={pkg.name} />
                    ) : (
                      <div className="icon-placeholder">
                        {categories.find(c => c.id === pkg.category)?.icon || '📦'}
                      </div>
                    )}
                  </div>
                  <div className="package-badges">
                    <span className="version-badge">v{pkg.version}</span>
                    <span className="type-badge">{pkg.type}</span>
                  </div>
                </div>

                <div className="package-body">
                  <h3 className="package-name">{pkg.name}</h3>
                  <p className="package-description">{pkg.description}</p>
                  
                  <div className="package-meta">
                    <div className="meta-item">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                      </svg>
                      <span>{pkg.author}</span>
                    </div>
                    <div className="meta-item">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                      </svg>
                      <span>{pkg.rating}</span>
                    </div>
                    <div className="meta-item">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                      </svg>
                      <span>{pkg.downloads}</span>
                    </div>
                  </div>

                  {pkg.tags && pkg.tags.length > 0 && (
                    <div className="package-tags">
                      {pkg.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                      {pkg.tags.length > 3 && (
                        <span className="tag-more">+{pkg.tags.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>

                <div className="package-footer">
                  <button
                    className="install-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleInstall(pkg)
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="7,10 12,15 17,10"/>
                      <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    安装
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 包详情模态框 */}
      {selectedPackage && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
            
            <div className="modal-header">
              <div className="modal-icon">
                {selectedPackage.icon_url ? (
                  <img src={selectedPackage.icon_url} alt={selectedPackage.name} />
                ) : (
                  <div className="icon-placeholder-large">
                    {categories.find(c => c.id === selectedPackage.category)?.icon || '📦'}
                  </div>
                )}
              </div>
              <div className="modal-info">
                <h2 className="modal-title">{selectedPackage.name}</h2>
                <p className="modal-id">{selectedPackage.id}</p>
                <div className="modal-badges">
                  <span className="version-badge">v{selectedPackage.version}</span>
                  <span className="type-badge">{selectedPackage.type}</span>
                </div>
              </div>
            </div>

            <div className="modal-body">
              <div className="modal-stats">
                <div className="stat-card">
                  <div className="stat-value">{selectedPackage.downloads}</div>
                  <div className="stat-label">下载量</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{selectedPackage.rating} ⭐</div>
                  <div className="stat-label">评分</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{selectedPackage.ratings_count || 0}</div>
                  <div className="stat-label">评价</div>
                </div>
              </div>

              <div className="modal-section">
                <h3 className="section-title">📝 描述</h3>
                <p className="section-content">{selectedPackage.description}</p>
                {selectedPackage.long_description && (
                  <div className="long-description">
                    {selectedPackage.long_description}
                  </div>
                )}
              </div>

              {selectedPackage.tags && selectedPackage.tags.length > 0 && (
                <div className="modal-section">
                  <h3 className="section-title">🏷️ 标签</h3>
                  <div className="tags-container">
                    {selectedPackage.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="modal-section">
                <h3 className="section-title">⚙️ 安装配置</h3>
                <pre className="config-code">
                  {JSON.stringify(selectedPackage.install_config, null, 2)}
                </pre>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={closeModal}>
                取消
              </button>
              <button 
                className="btn-primary"
                onClick={() => handleInstall(selectedPackage)}
              >
                安装 {selectedPackage.name}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MarketplaceView