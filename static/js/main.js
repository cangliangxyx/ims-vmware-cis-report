const tablesDiv = document.getElementById('tables');
const hostSelect = document.getElementById('hostSelect');

function friendlyFileName(filePath) {
    return filePath.split('/').pop().replace('.json', '');
}

async function loadHostOptions() {
    try {
        const response = await fetch('/all_hosts'); // Flask 后端返回所有 host.name 列表
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

async function loadJsonFilesForHost(targetHost) {
    tablesDiv.innerHTML = ""; // 切换 host 时清空之前表格
    try {
        const response = await fetch('/log_files');
        const jsonFiles = await response.json();

        for (const file of jsonFiles) {
            try {
                const res = await fetch(file);
                const data = await res.json();
                if (!data || data.length === 0) continue;

                const filteredData = data.filter(item => item.Host === targetHost || item.Host === null);
                if (filteredData.length === 0) continue;

                const h2 = document.createElement('h2');
                h2.textContent = friendlyFileName(file);
                tablesDiv.appendChild(h2);

                const table = document.createElement('table');
                const thead = document.createElement('thead');
                const tbody = document.createElement('tbody');

                const headerRow = document.createElement('tr');
                Object.keys(filteredData[0]).forEach(key => {
                    const th = document.createElement('th');
                    th.textContent = key;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                filteredData.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.style.backgroundColor = item.Status === "Pass" ? "#d4edda" : "#f8d7da";
                    Object.values(item).forEach(val => {
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

            } catch (err) {
                console.error("加载 JSON 文件失败:", file, err);
            }
        }

    } catch (err) {
        console.error("获取 JSON 文件列表失败:", err);
    }
}

// 当用户选择主机时加载数据
hostSelect.addEventListener('change', () => {
    const targetHost = hostSelect.value;
    if (targetHost) {
        loadJsonFilesForHost(targetHost);
    } else {
        tablesDiv.innerHTML = "";
    }
});

// 页面加载时先获取主机列表
loadHostOptions();
