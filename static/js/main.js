const tablesDiv = document.getElementById('tables');
const hostSelect = document.getElementById('hostSelect');
const statusSelect = document.getElementById('statusSelect');

let allData = []; // 保存所有 JSON 数据，方便筛选

function friendlyFileName(filePath) {
    return filePath.split('/').pop().replace('.json', '');
}

// 加载主机下拉列表
async function loadHostOptions() {
    try {
        const response = await fetch('/all_hosts');
        const hosts = await response.json();

        hosts.forEach(host => {
            const option = document.createElement('option');
            option.value = host;
            option.textContent = host;
            hostSelect.appendChild(option);
        });

    } catch (err) {
        console.error("获取主机列表失败:", err);
    }
}

// 加载所有 JSON 文件数据
async function loadAllJsonData() {
    tablesDiv.innerHTML = "";
    allData = [];

    try {
        const response = await fetch('/log_files');
        const jsonFiles = await response.json();

        for (const file of jsonFiles) {
            try {
                const res = await fetch(file);
                const data = await res.json();
                if (data && data.length > 0) {
                    data.forEach(item => item._file = friendlyFileName(file)); // 保存文件名
                    allData = allData.concat(data);
                }
            } catch (err) {
                console.error("加载 JSON 文件失败:", file, err);
            }
        }

        renderTables(); // 初始渲染
    } catch (err) {
        console.error("获取 JSON 文件列表失败:", err);
    }
}

// 渲染表格函数
function renderTables() {
    tablesDiv.innerHTML = "";

    const targetHost = hostSelect.value;
    const statusFilter = statusSelect.value;

    // 筛选数据
    let filteredData = allData;
    if (targetHost) {
        filteredData = filteredData.filter(item => item.Host === targetHost || item.Host === "ALL_HOSTS");
    }
    if (statusFilter) {
        filteredData = filteredData.filter(item => item.Status === statusFilter);
    }

    if (filteredData.length === 0) {
        tablesDiv.innerHTML = "<p>没有匹配的数据</p>";
        return;
    }

    // 按文件名分组
    const grouped = {};
    filteredData.forEach(item => {
        const file = item._file || "Unknown";
        if (!grouped[file]) grouped[file] = [];
        grouped[file].push(item);
    });

    for (const file in grouped) {
        const h2 = document.createElement('h2');
        h2.textContent = file;
        tablesDiv.appendChild(h2);

        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        // 表头
        const headerRow = document.createElement('tr');
        Object.keys(grouped[file][0]).forEach(key => {
            if (key === "_file") return; // 不显示内部字段
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // 表体
        grouped[file].forEach(item => {
            const tr = document.createElement('tr');
            tr.style.backgroundColor = item.Status === "Pass" ? "#d4edda" : "#f8d7da";

            Object.entries(item).forEach(([key, val]) => {
                if (key === "_file") return;
                const td = document.createElement('td');
                td.textContent = (typeof val === 'object' && val !== null)
                    ? JSON.stringify(val, null, 2)
                    : (val !== null ? val : '');
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        tablesDiv.appendChild(table);
    }
}

// 主机或状态变化时重新渲染
hostSelect.addEventListener('change', renderTables);
statusSelect.addEventListener('change', renderTables);

// 页面加载时初始化
loadHostOptions();
loadAllJsonData();


function renderTables() {
    tablesDiv.innerHTML = "";

    const targetHost = hostSelect.value;
    const statusFilter = statusSelect.value;

    // 筛选数据
    let filteredData = allData;
    if (targetHost) {
        filteredData = filteredData.filter(item => item.Host === targetHost || item.Host === "ALL_HOSTS");
    }
    if (statusFilter) {
        filteredData = filteredData.filter(item => item.Status === statusFilter);
    }

    // 统计 Pass / Fail
    let passCount = 0;
    let failCount = 0;
    filteredData.forEach(item => {
        if (item.Status === "Pass") passCount++;
        if (item.Status === "Fail") failCount++;
    });

    // 更新统计显示
    const statusSummaryDiv = document.getElementById("statusSummary");
    statusSummaryDiv.textContent = `Pass: ${passCount} / Fail: ${failCount}`;

    if (filteredData.length === 0) {
        tablesDiv.innerHTML = "<p>没有匹配的数据</p>";
        return;
    }

    // 按文件名分组
    const grouped = {};
    filteredData.forEach(item => {
        const file = item._file || "Unknown";
        if (!grouped[file]) grouped[file] = [];
        grouped[file].push(item);
    });

    for (const file in grouped) {
        const h2 = document.createElement('h2');
        h2.textContent = file;
        tablesDiv.appendChild(h2);

        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        // 表头
        const headerRow = document.createElement('tr');
        Object.keys(grouped[file][0]).forEach(key => {
            if (key === "_file") return; // 不显示内部字段
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // 表体
        grouped[file].forEach(item => {
            const tr = document.createElement('tr');
            tr.style.backgroundColor = item.Status === "Pass" ? "#d4edda" : "#f8d7da";

            Object.entries(item).forEach(([key, val]) => {
                if (key === "_file") return;
                const td = document.createElement('td');
                td.textContent = (typeof val === 'object' && val !== null)
                    ? JSON.stringify(val, null, 2)
                    : (val !== null ? val : '');
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        tablesDiv.appendChild(table);
    }
}

