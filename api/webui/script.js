// DOM Elements
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('nav ul li a');
const platformSelect = document.getElementById('platform');
const startCrawlerBtn = document.getElementById('start-crawler');
const stopCrawlerBtn = document.getElementById('stop-crawler');
const crawlerStatus = document.getElementById('crawler-status');
const createTaskBtn = document.getElementById('create-task');
const saveSettingsBtn = document.getElementById('save-settings');

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remove active class from all links and sections
        navLinks.forEach(l => l.classList.remove('active'));
        sections.forEach(s => s.classList.remove('active'));
        
        // Add active class to clicked link
        this.classList.add('active');
        
        // Show corresponding section
        const targetId = this.getAttribute('href').substring(1);
        document.getElementById(targetId).classList.add('active');
    });
});

// Initialize page
async function initPage() {
    await loadSystemStatus();
    await loadConfigOptions();
    setupEventListeners();
}

// Load system status
async function loadSystemStatus() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'ok') {
            document.getElementById('system-status').textContent = '正常运行';
        } else {
            document.getElementById('system-status').textContent = '异常';
        }
    } catch (error) {
        document.getElementById('system-status').textContent = '连接失败';
        console.error('Error loading system status:', error);
    }
}

// Load config options
async function loadConfigOptions() {
    try {
        const response = await fetch('/api/config/options');
        const data = await response.json();
        
        // Load current config
        const configResponse = await fetch('/api/config/current');
        const configData = await configResponse.json();
        
        // Update form fields
        document.getElementById('proxy-provider').value = configData.proxy.proxy_provider;
        document.getElementById('headless').checked = configData.browser.headless;
        document.getElementById('request-interval').value = configData.rate_limiting.request_interval;
        
    } catch (error) {
        console.error('Error loading config options:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Start crawler
    startCrawlerBtn.addEventListener('click', async function() {
        const platform = document.getElementById('platform').value;
        const crawlerType = document.getElementById('crawler-type').value;
        const query = document.getElementById('query').value;
        const maxResults = document.getElementById('max-results').value;
        const saveOption = document.getElementById('save-option').value;
        
        if (crawlerType === 'search' && !query) {
            alert('搜索模式需要输入搜索关键词');
            return;
        }
        
        crawlerStatus.textContent = '正在启动爬虫...';
        
        try {
            const response = await fetch('/api/crawler/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    platform,
                    crawler_type: crawlerType,
                    query,
                    max_results: parseInt(maxResults),
                    save_data_option: saveOption
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                crawlerStatus.textContent = '爬虫启动成功';
                setTimeout(() => {
                    crawlerStatus.textContent = '运行中...';
                }, 1000);
            } else {
                crawlerStatus.textContent = `启动失败: ${data.error}`;
            }
            
        } catch (error) {
            crawlerStatus.textContent = '启动失败: 网络错误';
            console.error('Error starting crawler:', error);
        }
    });
    
    // Stop crawler
    stopCrawlerBtn.addEventListener('click', async function() {
        crawlerStatus.textContent = '正在停止爬虫...';
        
        try {
            const response = await fetch('/api/crawler/stop', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                crawlerStatus.textContent = '爬虫已停止';
            } else {
                crawlerStatus.textContent = `停止失败: ${data.error}`;
            }
            
        } catch (error) {
            crawlerStatus.textContent = '停止失败: 网络错误';
            console.error('Error stopping crawler:', error);
        }
    });
    
    // Create task
    createTaskBtn.addEventListener('click', async function() {
        const taskName = document.getElementById('task-name').value;
        const taskPlatform = document.getElementById('task-platform').value;
        const taskType = document.getElementById('task-type').value;
        const taskQuery = document.getElementById('task-query').value;
        const taskInterval = document.getElementById('task-interval').value;
        
        if (!taskName) {
            alert('请输入任务名称');
            return;
        }
        
        if (taskType === 'search' && !taskQuery) {
            alert('搜索模式需要输入搜索关键词');
            return;
        }
        
        try {
            const response = await fetch('/api/tasks/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: taskName,
                    platform: taskPlatform,
                    crawler_type: taskType,
                    query: taskQuery,
                    interval: parseInt(taskInterval)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('任务创建成功');
                loadTasks();
            } else {
                alert(`创建失败: ${data.error}`);
            }
            
        } catch (error) {
            alert('创建失败: 网络错误');
            console.error('Error creating task:', error);
        }
    });
    
    // Save settings
    saveSettingsBtn.addEventListener('click', async function() {
        const proxyEnabled = document.getElementById('proxy-enabled').checked;
        const proxyProvider = document.getElementById('proxy-provider').value;
        const proxyApiKey = document.getElementById('proxy-api-key').value;
        const headless = document.getElementById('headless').checked;
        const requestInterval = document.getElementById('request-interval').value;
        
        try {
            const response = await fetch('/api/config/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    use_proxy: proxyEnabled,
                    proxy_provider: proxyProvider,
                    proxy_api_key: proxyApiKey,
                    headless: headless,
                    request_interval: parseFloat(requestInterval)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('设置保存成功');
            } else {
                alert(`保存失败: ${data.error}`);
            }
            
        } catch (error) {
            alert('保存失败: 网络错误');
            console.error('Error saving settings:', error);
        }
    });
}

// Load tasks
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        const taskTable = document.getElementById('task-table').querySelector('tbody');
        
        if (data.tasks && data.tasks.length > 0) {
            taskTable.innerHTML = '';
            
            data.tasks.forEach(task => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${task.task_id}</td>
                    <td>${task.name}</td>
                    <td>${task.platform}</td>
                    <td>${task.crawler_type}</td>
                    <td>${task.status}</td>
                    <td>${task.execution_count}</td>
                    <td>
                        <button class="btn-secondary" onclick="pauseTask('${task.task_id}')">暂停</button>
                        <button class="btn-secondary" onclick="resumeTask('${task.task_id}')">恢复</button>
                        <button class="btn-secondary" onclick="deleteTask('${task.task_id}')">删除</button>
                    </td>
                `;
                taskTable.appendChild(row);
            });
        } else {
            taskTable.innerHTML = '<tr><td colspan="7">暂无任务</td></tr>';
        }
        
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

// Task operations
async function pauseTask(taskId) {
    // Implementation for pausing task
    console.log('Pausing task:', taskId);
}

async function resumeTask(taskId) {
    // Implementation for resuming task
    console.log('Resuming task:', taskId);
}

async function deleteTask(taskId) {
    // Implementation for deleting task
    console.log('Deleting task:', taskId);
}

// Load data
async function loadData() {
    try {
        const platform = document.getElementById('data-platform').value;
        const limit = document.getElementById('data-limit').value;
        
        const response = await fetch(`/api/data?platform=${platform}&limit=${limit}`);
        const data = await response.json();
        
        const dataTable = document.getElementById('data-table').querySelector('tbody');
        
        if (data.data && data.data.length > 0) {
            dataTable.innerHTML = '';
            
            data.data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.platform}</td>
                    <td>${typeof item.data === 'object' ? '复杂数据' : item.data}</td>
                    <td>${new Date(item.created_at * 1000).toLocaleString()}</td>
                    <td>
                        <button class="btn-secondary" onclick="viewData(${item.id})">查看</button>
                        <button class="btn-secondary" onclick="deleteData(${item.id})">删除</button>
                    </td>
                `;
                dataTable.appendChild(row);
            });
        } else {
            dataTable.innerHTML = '<tr><td colspan="5">暂无数据</td></tr>';
        }
        
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Data operations
async function viewData(id) {
    // Implementation for viewing data
    console.log('Viewing data:', id);
}

async function deleteData(id) {
    // Implementation for deleting data
    console.log('Deleting data:', id);
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', initPage);