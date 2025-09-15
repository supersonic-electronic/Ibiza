/**
 * Futures Charts JavaScript
 * Interactive financial charting for Ibiza dashboard
 */

// Ensure Chart.js is properly configured
if (typeof Chart !== 'undefined') {
    // Set default options for better tooltips
    Chart.defaults.interaction.mode = 'index';
    Chart.defaults.interaction.intersect = false;
    Chart.defaults.plugins.tooltip.enabled = true;
}

class FuturesChartsInterface {
    constructor() {
        this.availableMarkets = [];
        this.availableContracts = [];
        this.selectedMarket = null;
        this.selectedContracts = new Set();
        this.chartInstance = null;
        this.chartData = null;
        
        this.init();
    }

    async init() {
        await this.loadAvailableMarkets();
        this.setupEventListeners();
        this.updateControlStates();
    }

    async loadAvailableMarkets() {
        try {
            const response = await fetch('/api/available-futures-markets');
            if (response.ok) {
                const data = await response.json();
                this.availableMarkets = data.markets || data; // Handle both response formats
                this.renderMarketList(this.availableMarkets);
            } else {
                // Use fallback mock data for demonstration
                this.availableMarkets = this.getMockMarkets();
                this.renderMarketList(this.availableMarkets);
            }
        } catch (error) {
            console.error('Error loading markets:', error);
            // Use mock data as fallback
            this.availableMarkets = this.getMockMarkets();
            this.renderMarketList(this.availableMarkets);
        }
    }

    getMockMarkets() {
        return [
            // Equity Index Futures
            { symbol: 'ES1', name: 'S&P 500 E-mini', type: 'equity', exchange: 'CME', description: 'S&P 500 Index Future' },
            { symbol: 'NQ1', name: 'NASDAQ 100 E-mini', type: 'equity', exchange: 'CME', description: 'NASDAQ 100 Index Future' },
            { symbol: 'RTY1', name: 'Russell 2000 E-mini', type: 'equity', exchange: 'CME', description: 'Russell 2000 Index Future' },
            { symbol: 'YM1', name: 'Dow Jones E-mini', type: 'equity', exchange: 'CME', description: 'Dow Jones Industrial Average Future' },
            
            // Commodity Futures
            { symbol: 'CL1', name: 'Crude Oil WTI', type: 'commodity', exchange: 'NYMEX', description: 'West Texas Intermediate Crude Oil' },
            { symbol: 'GC1', name: 'Gold', type: 'commodity', exchange: 'COMEX', description: 'Gold Futures' },
            { symbol: 'SI1', name: 'Silver', type: 'commodity', exchange: 'COMEX', description: 'Silver Futures' },
            { symbol: 'NG1', name: 'Natural Gas', type: 'commodity', exchange: 'NYMEX', description: 'Natural Gas Futures' },
            { symbol: 'HG1', name: 'Copper', type: 'commodity', exchange: 'COMEX', description: 'Copper Futures' },
            { symbol: 'C 1', name: 'Corn', type: 'commodity', exchange: 'CBOT', description: 'Corn Futures' },
            { symbol: 'S 1', name: 'Soybeans', type: 'commodity', exchange: 'CBOT', description: 'Soybean Futures' },
            { symbol: 'W 1', name: 'Wheat', type: 'commodity', exchange: 'CBOT', description: 'Wheat Futures' },
            
            // Currency Futures
            { symbol: 'DX1', name: 'US Dollar Index', type: 'currency', exchange: 'ICE', description: 'US Dollar Index Future' },
            { symbol: '6E1', name: 'EUR/USD', type: 'currency', exchange: 'CME', description: 'Euro FX Future' },
            { symbol: '6J1', name: 'JPY/USD', type: 'currency', exchange: 'CME', description: 'Japanese Yen Future' },
            
            // Fixed Income
            { symbol: 'ZB1', name: '30-Year T-Bond', type: 'fixed_income', exchange: 'CBOT', description: '30-Year Treasury Bond Future' },
            { symbol: 'ZN1', name: '10-Year T-Note', type: 'fixed_income', exchange: 'CBOT', description: '10-Year Treasury Note Future' },
            { symbol: 'ZF1', name: '5-Year T-Note', type: 'fixed_income', exchange: 'CBOT', description: '5-Year Treasury Note Future' }
        ];
    }

    setupEventListeners() {
        // Market search
        document.getElementById('marketSearch').addEventListener('input', (e) => {
            this.handleMarketSearch(e.target.value);
        });

        // Category filters
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleCategoryFilter(e.target.dataset.category);
            });
        });

        // Contract filters
        document.getElementById('contractYear').addEventListener('change', () => {
            this.filterContracts();
        });

        document.getElementById('contractMonth').addEventListener('change', () => {
            this.filterContracts();
        });

        // Chart configuration
        document.getElementById('chartType').addEventListener('change', () => {
            this.updateChartIfLoaded();
        });

        document.getElementById('priceType').addEventListener('change', () => {
            this.updateChartIfLoaded();
        });

        document.getElementById('dateRange').addEventListener('change', (e) => {
            const customRange = document.getElementById('customDateRange');
            if (e.target.value === 'custom') {
                customRange.style.display = 'block';
                this.setDefaultCustomDates();
            } else {
                customRange.style.display = 'none';
            }
        });

        // Chart actions
        document.getElementById('loadChart').addEventListener('click', () => {
            this.loadChart();
        });

        document.getElementById('resetChart').addEventListener('click', () => {
            this.resetChart();
        });

        document.getElementById('exportChart').addEventListener('click', () => {
            this.exportChart();
        });

        document.getElementById('toggleGrid').addEventListener('click', () => {
            this.toggleGrid();
        });

        document.getElementById('zoomReset').addEventListener('click', () => {
            this.resetZoom();
        });

        // Refresh contracts button
        document.getElementById('refreshContracts').addEventListener('click', () => {
            this.refreshContractData();
        });

        // Date inputs for custom range
        document.getElementById('startDate').addEventListener('change', () => {
            this.updateChartIfLoaded();
        });

        document.getElementById('endDate').addEventListener('change', () => {
            this.updateChartIfLoaded();
        });
    }

    handleMarketSearch(query) {
        if (!query.trim()) {
            this.renderMarketList(this.availableMarkets);
            return;
        }
        
        const filtered = this.availableMarkets.filter(market => 
            market.symbol.toLowerCase().includes(query.toLowerCase()) ||
            (market.name && market.name.toLowerCase().includes(query.toLowerCase())) ||
            (market.description && market.description.toLowerCase().includes(query.toLowerCase())) ||
            (market.display_name && market.display_name.toLowerCase().includes(query.toLowerCase())) ||
            (market.type && market.type.toLowerCase().includes(query.toLowerCase()))
        );
        this.renderMarketList(filtered);
    }

    handleCategoryFilter(category) {
        // Update active category button
        document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-category="${category}"]`).classList.add('active');

        // Filter markets
        const filtered = category === 'all' 
            ? this.availableMarkets 
            : this.availableMarkets.filter(market => market.type === category);
        
        this.renderMarketList(filtered);
    }

    renderMarketList(markets) {
        const marketList = document.getElementById('marketList');
        
        if (markets.length === 0) {
            marketList.innerHTML = '<div class="empty-state">No markets match your search</div>';
            marketList.classList.add('empty');
            return;
        }
        
        marketList.classList.remove('empty', 'loading');
        
        marketList.innerHTML = markets.map(market => `
            <div class="market-item" data-symbol="${market.symbol}">
                <div class="market-info">
                    <div class="market-name">${market.display_name || market.symbol.replace(' Comdty', '').replace(' Index', '')}</div>
                    <div class="market-description">${market.name || market.description || market.symbol}</div>
                </div>
                <div class="market-type">${market.type.replace('_', ' ').toUpperCase()}</div>
            </div>
        `).join('');

        // Add event listeners to market items
        marketList.querySelectorAll('.market-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.selectMarket(item.dataset.symbol);
            });
        });
    }

    async selectMarket(symbol) {
        // Clear previous selection
        document.querySelectorAll('.market-item').forEach(item => item.classList.remove('selected'));
        document.querySelector(`[data-symbol="${symbol}"]`).classList.add('selected');
        
        this.selectedMarket = symbol;
        this.selectedContracts.clear();
        
        // Update UI
        this.updateSelectedMarketDisplay();
        this.updateSelectedContractsDisplay();
        
        // Load contracts for this market
        await this.loadContractsForMarket(symbol);
        
        // Load metadata for this market
        await this.loadMarketMetadata(symbol);
        
        this.updateControlStates();
    }

    async loadContractsForMarket(symbol) {
        const contractList = document.getElementById('contractList');
        contractList.classList.add('loading');
        contractList.innerHTML = '<div class="loading-indicator">Loading contracts...</div>';

        try {
            // Add cache-busting timestamp to prevent stale data
            const cacheBuster = Date.now();
            const response = await fetch(`/api/futures-contracts/${symbol}?t=${cacheBuster}`, {
                headers: {
                    'Cache-Control': 'no-cache, no-store, must-revalidate'
                }
            });
            if (response.ok) {
                const data = await response.json();
                this.availableContracts = data.contracts || data; // Handle both response formats
            } else {
                // Generate mock contracts for demonstration
                this.availableContracts = this.generateMockContracts(symbol);
            }
        } catch (error) {
            console.error('Error loading contracts:', error);
            this.availableContracts = this.generateMockContracts(symbol);
        }

        this.populateContractYears();
        this.renderContractList(this.availableContracts);
        contractList.classList.remove('loading');
        
        // Update contract count
        document.getElementById('contractCount').textContent = `${this.availableContracts.length} contracts`;
    }

    async loadMarketMetadata(symbol) {
        try {
            const response = await fetch(`/api/futures-metadata/${symbol}`);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    this.displayMarketMetadata(data.metadata);
                } else {
                    console.error('Error loading metadata:', data.error);
                    this.hideMarketMetadata();
                }
            } else {
                console.log('Metadata not available for', symbol);
                this.hideMarketMetadata();
            }
        } catch (error) {
            console.error('Error loading metadata:', error);
            this.hideMarketMetadata();
        }
    }

    displayMarketMetadata(metadata) {
        // Show the metadata section
        const metadataSection = document.getElementById('futuresMetadata');
        metadataSection.style.display = 'block';

        // Update market name
        document.getElementById('marketName').textContent = metadata.long_name || metadata.market;

        // Update contract specifications
        document.getElementById('contractSize').textContent = metadata.contract_size;
        document.getElementById('tickSize').textContent = metadata.tick_size;
        document.getElementById('tickValue').textContent = metadata.tick_value;
        document.getElementById('pointValue').textContent = metadata.point_value;

        // Update trading information
        const exchangeElement = document.getElementById('exchange');
        exchangeElement.textContent = metadata.exchange;
        exchangeElement.className = 'metadata-value exchange';

        document.getElementById('tradingHours').textContent = metadata.trading_hours;
        document.getElementById('tradingHours').className = 'metadata-value trading-hours';
        
        document.getElementById('tradingMonths').textContent = metadata.trading_months;
        document.getElementById('category').textContent = metadata.category;

        // Update market data
        document.getElementById('availableContracts').textContent = `${metadata.total_contracts} contracts`;
        document.getElementById('dataRange').textContent = metadata.data_range;
        document.getElementById('priceMultiplier').textContent = metadata.price_multiplier;
        
        const currencyElement = document.getElementById('currency');
        currencyElement.textContent = metadata.currency;
        currencyElement.className = 'metadata-value currency';
    }

    hideMarketMetadata() {
        document.getElementById('futuresMetadata').style.display = 'none';
    }

    async refreshContractData() {
        /**
         * Force refresh contract data by clearing cache and reloading
         */
        console.log('🔄 Refreshing contract data...');
        
        const refreshBtn = document.getElementById('refreshContracts');
        const originalHTML = refreshBtn.innerHTML;
        
        try {
            // Show loading state
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
            
            // Clear any cached data
            this.availableContracts = [];
            this.selectedContracts.clear();
            
            // Clear contract display
            const contractList = document.getElementById('contractList');
            contractList.innerHTML = '<div class="loading-indicator">Refreshing contracts...</div>';
            
            // Force reload contracts for current market
            if (this.selectedMarket) {
                await this.loadContractsForMarket(this.selectedMarket);
                console.log(`✅ Refreshed contracts for ${this.selectedMarket}`);
            }
            
        } catch (error) {
            console.error('❌ Error refreshing contracts:', error);
            // Show error state briefly
            refreshBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
            setTimeout(() => {
                refreshBtn.innerHTML = originalHTML;
                refreshBtn.disabled = false;
            }, 2000);
            return;
        }
        
        // Restore button state
        refreshBtn.innerHTML = originalHTML;
        refreshBtn.disabled = false;
    }

    generateMockContracts(symbol) {
        const contracts = [];
        const monthCodes = { 'H': 'Mar', 'M': 'Jun', 'U': 'Sep', 'Z': 'Dec' };
        const currentYear = new Date().getFullYear();
        
        // Generate contracts for current and next 3 years
        for (let year = currentYear - 2; year <= currentYear + 3; year++) {
            Object.entries(monthCodes).forEach(([code, month]) => {
                const yearSuffix = year.toString().slice(-1);
                // Clean symbol: ES1 Index -> ES, CL1 Comdty -> CL
                const baseSymbol = symbol.replace('1', '').replace(' Index', '').replace(' Comdty', '');
                const contractSymbol = `${baseSymbol}${code}${yearSuffix}`;
                const expiryDate = new Date(year, ['Mar', 'Jun', 'Sep', 'Dec'].indexOf(month) * 3 + 2, 15);
                
                contracts.push({
                    symbol: contractSymbol,
                    underlying: symbol,
                    month: code,
                    year: year,
                    expiry: expiryDate.toISOString().split('T')[0],
                    displayName: `${contractSymbol} (${month} ${year})`,
                    contractName: contractSymbol,
                    isActive: expiryDate > new Date()
                });
            });
        }
        
        // Sort by expiry date
        return contracts.sort((a, b) => new Date(a.expiry) - new Date(b.expiry));
    }

    populateContractYears() {
        const yearSelect = document.getElementById('contractYear');
        yearSelect.disabled = false;
        
        const years = [...new Set(this.availableContracts.map(c => c.year))].sort((a, b) => b - a);
        
        yearSelect.innerHTML = '<option value="">All Years</option>' +
            years.map(year => `<option value="${year}">${year}</option>`).join('');
    }

    filterContracts() {
        const selectedYear = document.getElementById('contractYear').value;
        const selectedMonth = document.getElementById('contractMonth').value;
        
        let filtered = this.availableContracts;
        
        // For charting purposes, we want to show ALL contracts (including expired ones)
        // Users should be able to chart historical data for any contract
        // Only filter out contracts that have no data or are clearly invalid
        
        // Optional: Filter out contracts that are too old (before 1990) to reduce clutter
        const minYear = 1990;
        filtered = filtered.filter(contract => {
            const contractYear = contract.year || new Date().getFullYear();
            return contractYear >= minYear;
        });
        
        if (selectedYear) {
            filtered = filtered.filter(contract => contract.year.toString() === selectedYear);
        }
        
        if (selectedMonth) {
            filtered = filtered.filter(contract => contract.month === selectedMonth);
        }
        
        this.renderContractList(filtered);
    }

    renderContractList(contracts) {
        const contractList = document.getElementById('contractList');
        document.getElementById('contractMonth').disabled = false;
        
        if (contracts.length === 0) {
            contractList.innerHTML = '<div class="empty-state">No contracts match your filters</div>';
            contractList.classList.add('empty');
            return;
        }
        
        contractList.classList.remove('empty', 'loading');
        
        contractList.innerHTML = contracts.map(contract => `
            <div class="contract-item ${this.selectedContracts.has(contract.symbol) ? 'selected' : ''}" 
                 data-symbol="${contract.symbol}">
                <div class="contract-info">
                    <div class="contract-name">${contract.symbol}</div>
                    <div class="contract-description">${contract.displayName}</div>
                </div>
                <div class="contract-expiry ${contract.isActive ? 'active' : 'expired'}">${contract.expiry_date || contract.expiry || 'N/A'}</div>
            </div>
        `).join('');

        // Add event listeners to contract items
        contractList.querySelectorAll('.contract-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.toggleContractSelection(item.dataset.symbol);
            });
        });
    }

    toggleContractSelection(symbol) {
        if (this.selectedContracts.has(symbol)) {
            this.selectedContracts.delete(symbol);
        } else {
            this.selectedContracts.add(symbol);
        }
        
        // Update UI
        this.renderContractList(this.availableContracts.filter(contract => {
            const selectedYear = document.getElementById('contractYear').value;
            const selectedMonth = document.getElementById('contractMonth').value;
            
            return (!selectedYear || contract.year.toString() === selectedYear) &&
                   (!selectedMonth || contract.month === selectedMonth);
        }));
        
        this.updateSelectedContractsDisplay();
        this.updateControlStates();
    }

    updateSelectedMarketDisplay() {
        const selectedMarket = document.getElementById('selectedMarket');
        const marketTag = document.getElementById('marketTag');
        
        if (this.selectedMarket) {
            const market = this.availableMarkets.find(m => m.symbol === this.selectedMarket);
            selectedMarket.style.display = 'block';
            marketTag.innerHTML = `
                <div class="tag">
                    <span>${market.symbol} - ${market.name}</span>
                    <i class="fas fa-times remove-tag" onclick="futuresCharts.clearMarketSelection()"></i>
                </div>
            `;
        } else {
            selectedMarket.style.display = 'none';
        }
    }

    updateSelectedContractsDisplay() {
        const selectedContracts = document.getElementById('selectedContracts');
        const contractTags = document.getElementById('contractTags');
        
        if (this.selectedContracts.size > 0) {
            selectedContracts.style.display = 'block';
            const tags = Array.from(this.selectedContracts).map(symbol => {
                const contract = this.availableContracts.find(c => c.symbol === symbol);
                return `
                    <div class="tag">
                        <span>${symbol} (${contract ? contract.displayName : 'Unknown'})</span>
                        <i class="fas fa-times remove-tag" onclick="futuresCharts.removeContractSelection('${symbol}')"></i>
                    </div>
                `;
            }).join('');
            
            contractTags.innerHTML = tags;
        } else {
            selectedContracts.style.display = 'none';
        }
    }

    clearMarketSelection() {
        this.selectedMarket = null;
        this.selectedContracts.clear();
        this.availableContracts = [];
        
        // Reset UI
        document.querySelectorAll('.market-item').forEach(item => item.classList.remove('selected'));
        document.getElementById('contractList').innerHTML = '';
        document.getElementById('contractYear').disabled = true;
        document.getElementById('contractMonth').disabled = true;
        document.getElementById('contractYear').value = '';
        document.getElementById('contractMonth').value = '';
        
        this.updateSelectedMarketDisplay();
        this.updateSelectedContractsDisplay();
        this.updateControlStates();
    }

    removeContractSelection(symbol) {
        this.selectedContracts.delete(symbol);
        this.updateSelectedContractsDisplay();
        this.renderContractList(this.availableContracts);
        this.updateControlStates();
    }

    updateControlStates() {
        const loadBtn = document.getElementById('loadChart');
        const canLoad = this.selectedMarket && this.selectedContracts.size > 0;
        
        loadBtn.disabled = !canLoad;
        
        // Update market status
        const marketStatus = document.getElementById('marketStatus');
        if (this.selectedMarket) {
            marketStatus.textContent = 'Market Selected';
            marketStatus.className = 'market-status selected';
        } else {
            marketStatus.textContent = 'Select Market';
            marketStatus.className = 'market-status';
        }
    }

    setDefaultCustomDates() {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 3);
        
        document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
        document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    }

    async loadChart() {
        if (!this.selectedMarket || this.selectedContracts.size === 0) return;
        
        this.showLoading(true);
        
        try {
            const dateRange = this.getDateRange();
            const priceType = document.getElementById('priceType').value;
            
            const response = await fetch('/api/futures-chart-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contracts: Array.from(this.selectedContracts).map(contractId => ({
                        market: this.selectedMarket,
                        contract_id: contractId
                    })),
                    date_range: {
                        start_date: dateRange.start,
                        end_date: dateRange.end
                    },
                    priceType: priceType
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('API Response:', data); // Debug log
                
                // Extract chart data from API response format
                if (data.chart_data && data.chart_data.length > 0) {
                    // Transform API response to expected format - handle multiple contracts properly
                    const selectedContractsArray = Array.from(this.selectedContracts);
                    this.chartData = [];
                    
                    // Process each contract separately if we have multiple contracts
                    if (selectedContractsArray.length > 1) {
                        // For multiple contracts, we should group data by contract
                        const contractDataMap = new Map();
                        
                        data.chart_data.forEach(market => {
                            if (market.data && market.data.length > 0) {
                                // Group data points by contract (security field)
                                market.data.forEach(point => {
                                    const contractCode = point.contract || point.security || 'Unknown';
                                    // Extract contract code (e.g., "ESH5 Index" -> "ESH5")
                                    const cleanContractCode = contractCode.replace(' Index', '').replace(' Comdty', '');
                                    
                                    if (!contractDataMap.has(cleanContractCode)) {
                                        contractDataMap.set(cleanContractCode, []);
                                    }
                                    contractDataMap.get(cleanContractCode).push(point);
                                });
                            }
                        });
                        
                        // Convert to chartData format
                        contractDataMap.forEach((prices, contractCode) => {
                            if (selectedContractsArray.includes(contractCode)) {
                                this.chartData.push({
                                    contract: contractCode,
                                    prices: prices
                                });
                            }
                        });
                    } else {
                        // Single contract - use existing logic
                        this.chartData = data.chart_data.map(market => {
                            const contractId = selectedContractsArray[0] || market.market;
                            return {
                                contract: contractId,
                                prices: market.data || []
                            };
                        });
                    }
                    console.log('Transformed chart data:', this.chartData); // Debug log
                } else {
                    console.log('No chart_data in response, using mock data');
                    // Generate mock data for demonstration
                    this.chartData = this.generateMockChartData();
                }
            } else {
                console.log('API response not OK, using mock data');
                // Generate mock data for demonstration
                this.chartData = this.generateMockChartData();
            }
            
            this.renderChart();
            this.updatePriceStats();
            
        } catch (error) {
            console.error('Error loading chart data:', error);
            // Use mock data as fallback
            this.chartData = this.generateMockChartData();
            this.renderChart();
            this.updatePriceStats();
        } finally {
            this.showLoading(false);
        }
    }

    getDateRange() {
        const dateRangeValue = document.getElementById('dateRange').value;
        // Use March 4, 2025 as end date since that's the latest available data
        const endDate = new Date('2025-03-04');
        let startDate = new Date('2025-03-04');
        
        switch (dateRangeValue) {
            case '1M':
                startDate.setMonth(endDate.getMonth() - 1);
                break;
            case '3M':
                startDate.setMonth(endDate.getMonth() - 3);
                break;
            case '6M':
                startDate.setMonth(endDate.getMonth() - 6);
                break;
            case '1Y':
                startDate.setFullYear(endDate.getFullYear() - 1);
                break;
            case 'custom':
                startDate = new Date(document.getElementById('startDate').value);
                // For custom, allow user to override endDate but default to data limit
                const customEndDate = document.getElementById('endDate').value;
                if (customEndDate) {
                    return {
                        start: startDate.toISOString().split('T')[0],
                        end: new Date(customEndDate).toISOString().split('T')[0]
                    };
                }
                break;
            case 'all':
                return { start: null, end: null };
        }
        
        return {
            start: startDate.toISOString().split('T')[0],
            end: endDate.toISOString().split('T')[0]
        };
    }

    generateMockChartData() {
        const data = [];
        const contracts = Array.from(this.selectedContracts);
        const dateRange = this.getDateRange();
        
        // Generate mock price data
        contracts.forEach(contract => {
            const prices = [];
            let currentPrice = 5500 + Math.random() * 1500; // Random starting price in ES1 range (5500-7000)
            const startDate = dateRange.start ? new Date(dateRange.start) : new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
            const endDate = dateRange.end ? new Date(dateRange.end) : new Date();
            
            for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
                // Skip weekends
                if (d.getDay() === 0 || d.getDay() === 6) continue;
                
                // Generate price movement
                const change = (Math.random() - 0.5) * 50;
                currentPrice += change;
                
                const bid = currentPrice - (Math.random() * 2);
                const ask = currentPrice + (Math.random() * 2);
                
                prices.push({
                    date: d.toISOString().split('T')[0],
                    contract: contract,
                    px_last: +currentPrice.toFixed(2),
                    px_bid: +bid.toFixed(2),
                    px_ask: +ask.toFixed(2),
                    volume: Math.floor(Math.random() * 100000) + 10000
                });
            }
            
            data.push({
                contract: contract,
                prices: prices
            });
        });
        
        return data;
    }

    renderChart() {
        const chartType = document.getElementById('chartType').value;
        const priceType = document.getElementById('priceType').value;
        
        // Destroy existing chart
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        
        // Show chart section
        document.getElementById('chartSection').style.display = 'block';
        
        // Show metadata section (if it has data)
        const metadataSection = document.getElementById('futuresMetadata');
        if (metadataSection && metadataSection.style.display !== 'none') {
            // Metadata is already displayed, keep it visible
        }
        
        // Prepare datasets
        const datasets = this.prepareChartDatasets(priceType);
        console.log('Prepared datasets:', datasets);
        
        if (datasets.length === 0) {
            console.error('No datasets prepared for chart');
            alert('No data available for the selected contracts');
            return;
        }
        
        // Create chart
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        const config = {
            type: chartType === 'candlestick' ? 'candlestick' : chartType,
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                hover: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: `${this.selectedMarket} - ${Array.from(this.selectedContracts).join(', ')}`,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        enabled: true,
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#333',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                        callbacks: {
                            title: function(tooltipItems) {
                                if (tooltipItems && tooltipItems.length > 0) {
                                    const item = tooltipItems[0];
                                    const date = new Date(item.parsed.x);
                                    return date.toLocaleDateString('en-US', {
                                        weekday: 'short',
                                        year: 'numeric',
                                        month: 'short',
                                        day: 'numeric'
                                    });
                                }
                                return '';
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += '$' + context.parsed.y.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'dd-MMM',
                                week: 'dd-MMM',
                                month: 'MMM yyyy',
                                quarter: 'MMM yyyy',
                                year: 'yyyy'
                            },
                            tooltipFormat: 'dd-MMM-yyyy'
                        },
                        ticks: {
                            source: 'auto',
                            autoSkip: true,
                            maxTicksLimit: 15,
                            callback: function(value, index, ticks) {
                                const date = new Date(value);
                                const day = date.getDate();
                                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                                const month = monthNames[date.getMonth()];
                                const year = date.getFullYear();
                                
                                // Check if this is January or the first/last tick
                                const isJanuary = date.getMonth() === 0;
                                const isFirstTick = index === 0;
                                const isLastTick = index === ticks.length - 1;
                                
                                // Check for year change
                                let isYearChange = false;
                                if (index > 0) {
                                    const prevDate = new Date(ticks[index - 1].value);
                                    isYearChange = prevDate.getFullYear() !== year;
                                }
                                
                                // Always show year for January, first tick, last tick, or year changes
                                if (isJanuary || isFirstTick || isLastTick || isYearChange) {
                                    return [`${day}-${month}`, `${year}`];
                                }
                                
                                return `${day}-${month}`;
                            },
                            font: function(context) {
                                // Style for multi-line labels
                                if (context.tick && context.tick.label && Array.isArray(context.tick.label)) {
                                    return {
                                        size: 11
                                    };
                                }
                                return {
                                    size: 10
                                };
                            },
                            color: function(context) {
                                // Make year labels stand out
                                if (context.tick && context.tick.label && Array.isArray(context.tick.label)) {
                                    return '#000';
                                }
                                return '#666';
                            }
                        },
                        grid: {
                            display: true,
                            drawBorder: true,
                            drawOnChartArea: true,
                            drawTicks: true,
                            color: function(context) {
                                // Stronger grid lines at year boundaries
                                if (context.tick && context.tick.label && Array.isArray(context.tick.label)) {
                                    return 'rgba(0, 0, 0, 0.2)';
                                }
                                return 'rgba(0, 0, 0, 0.05)';
                            },
                            lineWidth: function(context) {
                                // Thicker lines at year boundaries
                                if (context.tick && context.tick.label && Array.isArray(context.tick.label)) {
                                    return 2;
                                }
                                return 1;
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price ($)'
                        },
                        position: 'left'
                    }
                }
            }
        };
        
        try {
            this.chartInstance = new Chart(ctx, config);
            console.log('Chart created successfully');
            
            // Ensure Chart.js instance is attached to canvas
            ctx.canvas._chartjs = this.chartInstance;
            
            // Force chart update to ensure rendering
            this.chartInstance.update();
            
            // Update chart details
            this.updateChartDetails();
            
            // Log chart instance for debugging
            console.log('Chart instance attached:', ctx.canvas._chartjs !== undefined);
            
            // Ensure tooltips are enabled and working
            if (this.chartInstance.options.plugins.tooltip) {
                this.chartInstance.options.plugins.tooltip.enabled = true;
                this.chartInstance.options.interaction.intersect = false;
                this.chartInstance.options.interaction.mode = 'index';
            }
            
            // Update without animation to ensure immediate render
            this.chartInstance.update('none');
            
            // Add debug event listener
            ctx.canvas.addEventListener('mousemove', (e) => {
                const rect = ctx.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // Get tooltip state
                const tooltip = this.chartInstance.tooltip;
                if (tooltip._active && tooltip._active.length) {
                    console.log('Tooltip active with', tooltip._active.length, 'elements');
                }
            });
        } catch (error) {
            console.error('Error creating chart:', error);
            alert('Error creating chart: ' + error.message);
        }
    }

    prepareChartDatasets(priceType) {
        const datasets = [];
        const colors = ['#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#a855f7', '#ec4899'];
        
        this.chartData.forEach((contractData, index) => {
            const color = colors[index % colors.length];
            
            if (priceType === 'last' || priceType === 'all') {
                const validPrices = contractData.prices.filter(p => p.px_last !== null && p.px_last !== undefined);
                if (validPrices.length > 0) {
                    datasets.push({
                        label: `${contractData.contract} Last`,
                        data: validPrices.map(p => ({
                            x: new Date(p.date.split(' ')[0]), // Convert to Date object
                            y: p.px_last
                        })),
                        borderColor: color,
                        backgroundColor: color + '20',
                        tension: 0.1,
                        fill: false
                    });
                }
            }
            
            if (priceType === 'bid_ask' || priceType === 'all') {
                const validBids = contractData.prices.filter(p => p.px_bid !== null && p.px_bid !== undefined);
                const validAsks = contractData.prices.filter(p => p.px_ask !== null && p.px_ask !== undefined);
                
                if (validBids.length > 0) {
                    datasets.push({
                        label: `${contractData.contract} Bid`,
                        data: validBids.map(p => ({x: new Date(p.date.split(' ')[0]), y: p.px_bid})),
                        borderColor: color + 'AA',
                        backgroundColor: color + '10',
                        tension: 0.1,
                        fill: false,
                        borderDash: [5, 5]
                    });
                }
                
                if (validAsks.length > 0) {
                    datasets.push({
                        label: `${contractData.contract} Ask`,
                        data: validAsks.map(p => ({x: new Date(p.date.split(' ')[0]), y: p.px_ask})),
                        borderColor: color + 'CC',
                        backgroundColor: color + '10',
                        tension: 0.1,
                        fill: false,
                        borderDash: [2, 2]
                    });
                }
            }
        });
        
        return datasets;
    }

    updateChartDetails() {
        const details = document.getElementById('chartDetails');
        if (!details) return;
        
        const contracts = Array.from(this.selectedContracts);
        const dateRange = this.getDateRange();
        
        let dateText = 'All available data';
        if (dateRange.start && dateRange.end) {
            dateText = `${dateRange.start} to ${dateRange.end}`;
        }
        
        const totalDataPoints = this.chartData ? this.chartData.reduce((total, c) => total + (c.prices ? c.prices.length : 0), 0) : 0;
        
        details.innerHTML = `
            ${contracts.length} contract${contracts.length > 1 ? 's' : ''} • 
            ${totalDataPoints} data points • 
            ${dateText}
        `;
        
        // Make sure details are visible
        details.style.display = 'block';
    }

    updatePriceStats() {
        console.log('updatePriceStats called with chartData:', this.chartData); // Debug
        
        if (!this.chartData || this.chartData.length === 0) {
            console.log('No chartData available');
            return;
        }
        
        // Show stats section
        const priceStats = document.getElementById('priceStats');
        if (priceStats) {
            priceStats.style.display = 'block';
        }
        
        // Calculate stats for first contract (most recent)
        const firstContract = this.chartData[0];
        console.log('First contract:', firstContract); // Debug
        
        if (!firstContract || !firstContract.prices || firstContract.prices.length === 0) {
            console.warn('No price data available for statistics');
            // Set fallback values
            this.setFallbackPriceStats();
            return;
        }
        
        const latestPrice = firstContract.prices[firstContract.prices.length - 1];
        const previousPrice = firstContract.prices.length > 1 ? firstContract.prices[firstContract.prices.length - 2] : null;
        
        if (latestPrice && latestPrice.px_last !== null && latestPrice.px_last !== undefined) {
            const currentPriceElem = document.getElementById('currentPrice');
            if (currentPriceElem) {
                currentPriceElem.textContent = `$${parseFloat(latestPrice.px_last).toFixed(2)}`;
            }
            
            if (previousPrice && previousPrice.px_last !== null && previousPrice.px_last !== undefined) {
                const change = parseFloat(latestPrice.px_last) - parseFloat(previousPrice.px_last);
                const changePercent = (change / parseFloat(previousPrice.px_last)) * 100;
                const changeElement = document.getElementById('dailyChange');
                if (changeElement) {
                    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
                    changeElement.className = 'stat-value ' + (change >= 0 ? 'positive' : 'negative');
                }
            } else {
                const changeElement = document.getElementById('dailyChange');
                if (changeElement) {
                    changeElement.textContent = '--';
                    changeElement.className = 'stat-value';
                }
            }
            
            // Calculate daily high/low
            const sameDayPrices = firstContract.prices.filter(p => p.date === latestPrice.date && p.px_last !== null);
            if (sameDayPrices.length > 0) {
                const dayHigh = Math.max(...sameDayPrices.map(p => parseFloat(p.px_last)));
                const dayLow = Math.min(...sameDayPrices.map(p => parseFloat(p.px_last)));
                
                const dayHighElem = document.getElementById('dayHigh');
                const dayLowElem = document.getElementById('dayLow');
                if (dayHighElem) dayHighElem.textContent = `$${dayHigh.toFixed(2)}`;
                if (dayLowElem) dayLowElem.textContent = `$${dayLow.toFixed(2)}`;
            } else {
                // Use current price for high/low if no other data available
                const dayHighElem = document.getElementById('dayHigh');
                const dayLowElem = document.getElementById('dayLow');
                if (dayHighElem) dayHighElem.textContent = `$${parseFloat(latestPrice.px_last).toFixed(2)}`;
                if (dayLowElem) dayLowElem.textContent = `$${parseFloat(latestPrice.px_last).toFixed(2)}`;
            }
            
            // Volume and spread
            const volumeElem = document.getElementById('volume');
            if (volumeElem) {
                volumeElem.textContent = (latestPrice.volume && latestPrice.volume > 0) ? 
                    parseInt(latestPrice.volume).toLocaleString() : 'N/A';
            }
            
            const spreadElem = document.getElementById('bidAskSpread');
            if (spreadElem) {
                if (latestPrice.px_bid && latestPrice.px_ask && 
                    latestPrice.px_bid !== null && latestPrice.px_ask !== null) {
                    const spread = parseFloat(latestPrice.px_ask) - parseFloat(latestPrice.px_bid);
                    spreadElem.textContent = `$${spread.toFixed(2)}`;
                } else {
                    spreadElem.textContent = 'N/A';
                }
            }
        } else {
            // Set default values when no valid price data
            const elements = ['currentPrice', 'dailyChange', 'dayHigh', 'dayLow', 'volume', 'bidAskSpread'];
            elements.forEach(id => {
                const elem = document.getElementById(id);
                if (elem) elem.textContent = '--';
            });
        }
    }

    setFallbackPriceStats() {
        // Set fallback values when no price data is available
        const elements = ['currentPrice', 'dailyChange', 'dayHigh', 'dayLow', 'volume', 'bidAskSpread'];
        elements.forEach(id => {
            const elem = document.getElementById(id);
            if (elem) elem.textContent = '--';
        });
        
        // Reset daily change color
        const changeElement = document.getElementById('dailyChange');
        if (changeElement) {
            changeElement.className = 'stat-value';
        }
    }

    updateChartIfLoaded() {
        if (this.chartInstance && this.chartData) {
            this.renderChart();
        }
    }

    resetChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
        
        this.chartData = null;
        document.getElementById('chartSection').style.display = 'none';
    }

    exportChart() {
        if (this.chartInstance) {
            const url = this.chartInstance.toBase64Image('image/png', 1.0);
            const a = document.createElement('a');
            a.href = url;
            a.download = `futures_chart_${this.selectedMarket}_${new Date().toISOString().split('T')[0]}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    }

    toggleGrid() {
        if (this.chartInstance) {
            const gridDisplay = this.chartInstance.options.scales.x.grid.display;
            this.chartInstance.options.scales.x.grid.display = !gridDisplay;
            this.chartInstance.options.scales.y.grid.display = !gridDisplay;
            this.chartInstance.update();
        }
    }

    resetZoom() {
        if (this.chartInstance) {
            this.chartInstance.resetZoom();
        }
    }

    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.futuresCharts = new FuturesChartsInterface();
});