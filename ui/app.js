let state = {
  currentStep: 1,
  disks: [],
  selectedDisk: null,
  detectionData: null,
  firmwares: [],
  filteredFirmwares: [],
  selectedFirmware: null,
  flasherResult: null
};

// DOM Elements
const elements = {
  // Steps Nav
  stepTabs: [
    document.getElementById('stepTab1'),
    document.getElementById('stepTab2'),
    document.getElementById('stepTab3'),
    document.getElementById('stepTab4')
  ],
  sections: [
    document.getElementById('sectionStep1'),
    document.getElementById('sectionStep2'),
    document.getElementById('sectionStep3'),
    document.getElementById('sectionStep4')
  ],
  // Buttons
  btnRefreshDisks: document.getElementById('btnRefreshDisks'),
  btnOpenOutput: document.getElementById('btnOpenOutput'),
  btnProceedToDetect: document.getElementById('btnProceedToDetect'),
  btnBackToStep1: document.getElementById('btnBackToStep1'),
  btnRunProbe: document.getElementById('btnRunProbe'),
  btnProceedManualFw: document.getElementById('btnProceedManualFw'),
  btnProceedToFw: document.getElementById('btnProceedToFw'),
  btnBackToStep2: document.getElementById('btnBackToStep2'),
  btnProceedToFlash: document.getElementById('btnProceedToFlash'),
  btnBackToStep3: document.getElementById('btnBackToStep3'),
  btnBuildAndFlash: document.getElementById('btnBuildAndFlash'),
  btnOpenCurrentOutputFolder: document.getElementById('btnOpenCurrentOutputFolder'),
  btnToggleRawReport: document.getElementById('btnToggleRawReport'),
  btnToggleManualPaste: document.getElementById('btnToggleManualPaste'),
  manualPasteContainer: document.getElementById('manualPasteContainer'),
  manualReportText: document.getElementById('manualReportText'),
  btnParseManualReport: document.getElementById('btnParseManualReport'),
  btnClearLog: document.getElementById('btnClearLog'),
  // Containers & Inputs
  diskListGrid: document.getElementById('diskListGrid'),
  selectedDiskSummary: document.getElementById('selectedDiskSummary'),
  chkForceRomMode: document.getElementById('chkForceRomMode'),
  valController: document.getElementById('valController'),
  valVendor: document.getElementById('valVendor'),
  valFlashId: document.getElementById('valFlashId'),
  valFlashDesc: document.getElementById('valFlashDesc'),
  valCurrentFw: document.getElementById('valCurrentFw'),
  valDriveMode: document.getElementById('valDriveMode'),
  rawReportContainer: document.getElementById('rawReportContainer'),
  fwSearchInput: document.getElementById('fwSearchInput'),
  fwCountSummary: document.getElementById('fwCountSummary'),
  firmwareCandidateList: document.getElementById('firmwareCandidateList'),
  summaryTargetDisk: document.getElementById('summaryTargetDisk'),
  summaryBusType: document.getElementById('summaryBusType'),
  summarySelectedFw: document.getElementById('summarySelectedFw'),
  summaryFwNand: document.getElementById('summaryFwNand'),
  terminalLog: document.getElementById('terminalLog'),
  headerPickRow: document.getElementById('headerPickRow'),
  selHeaderType: document.getElementById('selHeaderType')
};

function desktopApi() {
  return (window.pywebview && window.pywebview.api) ? window.pywebview.api : null;
}

async function apiGetDisks() {
  const api = desktopApi();
  if (api) return await api.get_disks();
  const res = await fetch('/api/disks');
  return await res.json();
}

async function apiDetect(payload) {
  const api = desktopApi();
  if (api) {
    return await api.detect(payload.disk_number, payload.bus_type, payload.force_rom_mode, payload.wmi_name, payload.wmi_firmware);
  }
  const res = await fetch('/api/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return await res.json();
}

async function apiDetectManual(rawText) {
  const api = desktopApi();
  if (api) return await api.detect_manual(rawText);
  const res = await fetch('/api/detect/manual', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text: rawText })
  });
  return await res.json();
}

async function apiFirmwares(detection) {
  const api = desktopApi();
  if (api) return await api.firmwares(detection);
  const res = await fetch('/api/firmwares', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ detection: detection })
  });
  return await res.json();
}

async function apiFlashBuild(payload) {
  const api = desktopApi();
  if (api) {
    return await api.flash_build(payload.fw_path, payload.header_type, payload.vendor, payload.controller, payload.filename);
  }
  const res = await fetch('/api/flash/build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return await res.json();
}

async function apiFlashLaunch(payload) {
  const api = desktopApi();
  if (api) return await api.flash_launch(payload.exe_path, payload.disk_number);
  const res = await fetch('/api/flash/launch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return await res.json();
}

async function apiOpenFolder(folder) {
  const api = desktopApi();
  if (api) return await api.open_folder(folder);
  await fetch('/api/open-folder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ folder: folder })
  });
}

function busClass(busType) {
  const bus = (busType || '').toLowerCase();
  if (bus.includes('nvme')) return 'bus-nvme';
  if (bus.includes('usb')) return 'bus-usb';
  return 'bus-sata';
}

function canOpen(step) {
  if (step === 1) return true;
  if (step === 2) return !!state.selectedDisk;
  if (step === 3) return !!state.selectedDisk && !!state.detectionData;
  if (step === 4) return !!state.selectedFirmware;
  return false;
}

function markSteps() {
  elements.stepTabs.forEach((tab, idx) => {
    tab.classList.toggle('locked', !canOpen(idx + 1));
  });
}

function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Logging helper
function log(msg, type = 'info') {
  const line = document.createElement('div');
  line.className = `log-line log-${type}`;
  const time = new Date().toLocaleTimeString();
  line.textContent = `[${time}] ${msg}`;
  elements.terminalLog.appendChild(line);
  elements.terminalLog.scrollTop = elements.terminalLog.scrollHeight;
}

// Switch Steps
function goToStep(step) {
  if (step < 1 || step > 4) return;
  state.currentStep = step;

  elements.stepTabs.forEach((tab, idx) => {
    if (idx + 1 === step) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }
  });

  elements.sections.forEach((sec, idx) => {
    if (idx + 1 === step) {
      sec.style.display = 'flex';
    } else {
      sec.style.display = 'none';
    }
  });
  markSteps();

  if (step === 2 && state.selectedDisk && !state.detectionData) {
    elements.valController.textContent = state.selectedDisk.name || "—";
    elements.valVendor.textContent = state.selectedDisk.bridge_name ? 
      `Через мост: ${state.selectedDisk.bridge_name}` : 
      (state.selectedDisk.bus_type ? `Шина: ${state.selectedDisk.bus_type}` : "—");
    elements.valCurrentFw.textContent = state.selectedDisk.firmware || "—";
    elements.valFlashId.textContent = "Нажмите 'Запустить опрос' для чтения FID";
    elements.valFlashDesc.textContent = "Flash память ожидает опроса";
    elements.valDriveMode.textContent = "Режим: Ожидание";
    elements.valDriveMode.style.color = "var(--text-muted)";
  }
}

// 1. Fetch Disks
async function loadDisks() {
  log("Сканирование физических дисков в системе...", "info");
  elements.diskListGrid.innerHTML = `
    <div style="padding: 24px; color: var(--text-muted); text-align: center; grid-column: 1/-1;">
      Опрос системных дисков...
    </div>
  `;

  try {
    const data = await apiGetDisks();
    state.disks = data.disks || [];
    renderDisks();
    log(`Найдено накопителей: ${state.disks.length}`, "success");
  } catch (err) {
    log(`Ошибка сканирования дисков: ${err.message}`, "err");
    elements.diskListGrid.innerHTML = `
      <div style="padding: 24px; color: var(--accent-rose); text-align: center; grid-column: 1/-1;">
        Не удалось загрузить накопители: ${err.message}
      </div>
    `;
  }
}

function renderDisks() {
  elements.diskListGrid.innerHTML = '';
  if (state.disks.length === 0) {
    elements.diskListGrid.innerHTML = '<div style="color: var(--text-muted);">Накопители не обнаружены.</div>';
    return;
  }

  state.disks.forEach(disk => {
    const card = document.createElement('div');
    card.className = `disk-card ${disk.is_system ? 'is-system' : ''}`;
    if (state.selectedDisk && state.selectedDisk.number === disk.number) {
      card.classList.add('selected');
    }

    const busBadge = busClass(disk.bus_type);
    const safeName = escapeHtml(disk.name);
    const safeBus = escapeHtml(disk.bus_type || '—');
    const safeSize = escapeHtml(disk.size_formatted);
    const safeFw = escapeHtml(disk.firmware || '—');
    const safeBridge = disk.bridge_name ? escapeHtml(disk.bridge_name) : '';
    const safeLetters = (disk.drive_letters && disk.drive_letters.length > 0) ? escapeHtml(disk.drive_letters.join(', ')) : '';

    card.innerHTML = `
      <div class="disk-header-row">
        <span class="disk-index">Диск ${disk.number}</span>
        <span class="bus-badge ${busBadge}">${safeBus}</span>
      </div>
      <div class="disk-name" title="${safeName}">${safeName}</div>
      <div class="disk-meta">
        <span>Объем: <b>${safeSize}</b></span>
        <span>FW: <b>${safeFw}</b></span>
      </div>
      ${safeBridge ? 
        `<div style="font-size: 0.74rem; color: #38bdf8; margin-top: 3px;">🔌 Мост: <b>${safeBridge}</b></div>` : ''}
      ${safeLetters ? 
        `<div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">Разделы: <b>${safeLetters}</b></div>` : ''}
      ${disk.is_system ? `
        <div class="disk-system-warn">
          <span>🛡️</span>
          <span>Системный диск (C:) — Защищен</span>
        </div>
      ` : ''}
    `;

    card.addEventListener('click', () => {
      if (disk.is_system) {
        log(`Диск ${disk.number} (${disk.name}) содержит систему Windows и защищен от прошивки!`, "warn");
        return;
      }
      selectDisk(disk);
    });

    elements.diskListGrid.appendChild(card);
  });
}

function selectDisk(disk) {
  state.selectedDisk = disk;
  elements.selectedDiskSummary.textContent = `Выбран: Диск ${disk.number} (${disk.name}, ${disk.size_formatted})`;
  elements.btnProceedToDetect.disabled = false;
  renderDisks();
  markSteps();
  log(`Выбран целевой накопитель: Диск ${disk.number} [${disk.bus_type}] ${disk.name}`, "info");
}

// 2. Probe Controller & Flash ID
async function runProbe() {
  if (!state.selectedDisk) return;
  const diskNum = state.selectedDisk.number;
  const busType = state.selectedDisk.bus_type;
  const forceRom = elements.chkForceRomMode.checked;

  elements.btnRunProbe.disabled = true;
  elements.btnRunProbe.textContent = "⏳ Опрос чипов...";
  log(`Запуск опроса контроллера и памяти на Диске ${diskNum} (${busType})...`, "info");

  try {
    const result = await apiDetect({
      disk_number: diskNum,
      bus_type: busType,
      force_rom_mode: forceRom,
      wmi_name: state.selectedDisk?.name || '',
      wmi_firmware: state.selectedDisk?.firmware || ''
    });
    if (result.success && result.data) {
      state.detectionData = result.data;
      displayDetectionResult(result.data);
      log(`Успешно определен: ${result.data.vendor} ${result.data.controller || ''}`, "success");
      elements.btnProceedToFw.disabled = false;
      markSteps();
    } else {
      if (result.data) {
        displayDetectionResult(result.data);
      }
      elements.rawReportContainer.style.display = 'block';
      elements.btnToggleRawReport.textContent = 'Скрыть сырой отчет 📄';
      if (result.raw) {
        elements.rawReportContainer.textContent = (result.message ? (result.message + "\n\n--- СЫРОЙ ОТЧЕТ УТИЛИТЫ ---\n") : "") + result.raw;
      } else {
        elements.rawReportContainer.textContent = result.message || "Утилиты не вернули ответа. Проверьте подключение накопителя.";
      }
      log(`Опрос завершен: ${result.message || 'Контроллер не ответил'}`, "warn");
    }
  } catch (err) {
    log(`Ошибка опроса накопителя: ${err.message}`, "err");
  } finally {
    elements.btnRunProbe.disabled = false;
    elements.btnRunProbe.textContent = "⚡ Запустить опрос";
  }
}

function displayDetectionResult(data) {
  if (data.real_model) {
    elements.valController.textContent = `${data.controller || 'Контроллер'} (${data.real_model})`;
  } else {
    elements.valController.textContent = data.controller || state.selectedDisk?.name || "Неизвестный";
  }
  elements.valVendor.textContent = data.vendor || (state.selectedDisk ? `Шина: ${state.selectedDisk.bus_type}` : "Phison / SMI / Maxio");
  elements.valFlashId.textContent = data.flash_id || "Flash ID не получен";
  elements.valFlashDesc.textContent = data.flash_desc || "Flash память не определена";
  elements.valCurrentFw.textContent = data.fw_version || state.selectedDisk?.firmware || "—";

  if (data.rom_mode) {
    elements.valDriveMode.textContent = "Режим: ROM Mode (Safe Mode)";
    elements.valDriveMode.style.color = "#f59e0b";
  } else if (data.is_oem_unsupported) {
    elements.valDriveMode.textContent = "Режим: Заводской OEM SSD";
    elements.valDriveMode.style.color = "#38bdf8";
  } else if (data.vendor && data.vendor.includes("USB-мост")) {
    elements.valDriveMode.textContent = "Режим: USB-мост перехватывает команды";
    elements.valDriveMode.style.color = "#f43f5e";
  } else {
    elements.valDriveMode.textContent = "Режим: Normal / Operational";
    elements.valDriveMode.style.color = "#10b981";
  }

  if (data.raw) {
    elements.rawReportContainer.textContent = data.raw;
  }
}

// 3. Firmware Matching
async function loadFirmwares() {
  log("Поиск и ранжирование совместимых прошивок...", "info");
  elements.firmwareCandidateList.innerHTML = '<div style="color: var(--text-muted); padding: 16px;">Поиск в локальной базе прошивок...</div>';

  try {
    const data = await apiFirmwares(state.detectionData);
    state.firmwares = data.firmwares || [];
    state.filteredFirmwares = [...state.firmwares];
    renderFirmwares();
    log(`Локальных прошивок в папке firmware: ${state.firmwares.length}`, "success");
  } catch (err) {
    log(`Ошибка подбора прошивок: ${err.message}`, "err");
  }
}

function renderFirmwares() {
  elements.firmwareCandidateList.innerHTML = '';
  elements.fwCountSummary.textContent = `Найдено: ${state.filteredFirmwares.length}`;

  if (state.filteredFirmwares.length === 0) {
    elements.firmwareCandidateList.innerHTML = '<div style="color: var(--text-muted); padding: 16px;">Нет подходящих файлов прошивок по запросу.</div>';
    return;
  }

  state.filteredFirmwares.forEach(fw => {
    const card = document.createElement('div');
    card.className = 'fw-card';
    if (state.selectedFirmware && (state.selectedFirmware.path === fw.path || state.selectedFirmware.filename === fw.filename)) {
      card.classList.add('selected');
    }

    const badgeClass = fw.badge_color === 'emerald' ? 'tag-emerald' : 
                       (fw.badge_color === 'blue' ? 'tag-blue' : 'tag-gray');

    const reasonsHtml = (fw.match_reasons && fw.match_reasons.length > 0)
      ? `<div style="font-size: 0.76rem; color: #34d399; margin-top: 4px; display: flex; flex-wrap: wrap; gap: 6px;">
           ${fw.match_reasons.map(r => `<span style="background: rgba(16, 185, 129, 0.15); padding: 2px 8px; border-radius: 4px;">✓ ${escapeHtml(r)}</span>`).join('')}
         </div>`
      : '';

    const actionHtml = `<button class="btn btn-secondary btn-select-fw" style="font-size: 0.8rem; padding: 6px 14px;">Выбрать</button>`;
    const safeFilename = escapeHtml(fw.filename);
    const safeBadge = escapeHtml(fw.badge || 'Совместимая');
    const safeTargetNand = escapeHtml(fw.target_nand || 'Phison / SMI');
    const safeSizeStr = escapeHtml(fw.size_str);
    const safeGen = fw.generation ? escapeHtml(fw.generation) : '';

    card.innerHTML = `
      <div class="fw-info" style="flex: 1;">
        <div class="fw-title">
          <span>${safeFilename}</span>
          <span class="badge-tag ${badgeClass}">${safeBadge}</span>
        </div>
        <div class="fw-meta" style="margin-top: 4px;">
          <span>Целевая память: <b>${safeTargetNand}</b></span>
          <span>Размер: ${safeSizeStr}</span>
          ${safeGen ? `<span>Серия: ${safeGen}</span>` : ''}
          ${fw.size_supported === false ? `<span style="color:#f87171;">Размер не поддерживается сборщиком S11</span>` : ''}
          ${fw.is_local && fw.vendor === 'Phison' && !fw.header_type ? `<span style="color:#fbbf24;">Заголовок нужно выбрать вручную</span>` : ''}
        </div>
        ${reasonsHtml}
      </div>
      <div>
        ${actionHtml}
      </div>
    `;

    card.addEventListener('click', () => selectFirmware(fw));

    elements.firmwareCandidateList.appendChild(card);
  });
}

function selectFirmware(fw) {
  state.selectedFirmware = fw;
  elements.btnProceedToFlash.disabled = false;
  markSteps();
  renderFirmwares();
  log(`Выбрана прошивка: ${fw.filename} [${fw.target_nand}]`, "info");
}

// 4. Build & Launch Flasher
async function buildAndLaunchFlasher() {
  if (!state.selectedFirmware) {
    log("Прошивка не выбрана!", "warn");
    return;
  }

  const fw = state.selectedFirmware;
  if (fw.is_local && fw.vendor === 'Phison' && fw.size_supported === false) {
    log("Этот файл нельзя собрать: размер не входит в 1479168, 1544704 или 1547776 байт.", "warn");
    return;
  }
  let headerType = fw.header_type || '';
  if (fw.vendor === 'Phison' && fw.is_local) {
    headerType = (elements.selHeaderType && elements.selHeaderType.value) || headerType;
    if (!headerType) {
      log("Выберите тип заголовка S11: Toshiba (0t), Micron (0m) или Micron new (0n).", "warn");
      return;
    }
  }

  elements.btnBuildAndFlash.disabled = true;
  elements.btnBuildAndFlash.textContent = "⏳ Сборка прошивальщика...";
  log(`Начало подготовки прошивальщика для ${fw.filename}...`, "info");

  try {
    const result = await apiFlashBuild({
      fw_path: fw.path,
      header_type: headerType,
      vendor: fw.vendor || 'Phison',
      controller: fw.controller || '',
      filename: fw.filename || ''
    });
    if (result.success) {
      state.flasherResult = result;
      
      if (result.flasher_exe) {
        log(`Прошивальщик подготовлен в ${result.flasher_exe}!`, "success");
        log("Запуск прошивальщика с правами Администратора...", "info");
        const launchData = await apiFlashLaunch({
          exe_path: result.flasher_exe,
          disk_number: state.selectedDisk ? state.selectedDisk.number : null
        });
        if (launchData.success) {
          log(launchData.message || `Прошивальщик запущен в отдельном окне.`, "success");
        } else {
          log(`Ошибка запуска: ${launchData.message}`, "err");
        }
      } else {
        log(result.message || `Пакет подготовлен в ${result.output_dir}`, "success");
      }
    } else {
      log(`Ошибка подготовки: ${result.message}`, "err");
    }
  } catch (err) {
    log(`Исключение при подготовке: ${err.message}`, "err");
  } finally {
    const blocked = fw.is_local && fw.vendor === 'Phison' && fw.size_supported === false;
    elements.btnBuildAndFlash.disabled = blocked;
    if (fw.vendor === 'Maxio') {
      elements.btnBuildAndFlash.textContent = '🚀 Подготовить локальный Maxio MPTool';
    } else if (fw.vendor === 'Silicon Motion') {
      elements.btnBuildAndFlash.textContent = '🚀 Подготовить локальный SMI MPTool';
    } else {
      elements.btnBuildAndFlash.textContent = '🚀 Собрать и запустить fw.exe';
    }
  }
}

// Event Listeners
elements.stepTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const step = parseInt(tab.getAttribute('data-step'));
    if (!canOpen(step)) {
      log("Сначала завершите предыдущий шаг.", "warn");
      return;
    }
    goToStep(step);
  });
});

elements.btnRefreshDisks.addEventListener('click', loadDisks);

elements.btnOpenOutput.addEventListener('click', async () => {
  await apiOpenFolder('output');
});

elements.btnOpenCurrentOutputFolder.addEventListener('click', async () => {
  const folder = state.flasherResult ? state.flasherResult.output_dir : 'output';
  await apiOpenFolder(folder);
});

elements.btnProceedToDetect.addEventListener('click', () => {
  goToStep(2);
  runProbe();
});

elements.btnBackToStep1.addEventListener('click', () => goToStep(1));
elements.btnRunProbe.addEventListener('click', runProbe);

elements.btnToggleRawReport.addEventListener('click', () => {
  const isHidden = elements.rawReportContainer.style.display === 'none';
  elements.rawReportContainer.style.display = isHidden ? 'block' : 'none';
  elements.btnToggleRawReport.textContent = isHidden ? 'Скрыть сырой отчет 📄' : 'Показать сырой отчет утилиты 📄';
});

if (elements.btnToggleManualPaste) {
  elements.btnToggleManualPaste.addEventListener('click', () => {
    const isHidden = elements.manualPasteContainer.style.display === 'none';
    elements.manualPasteContainer.style.display = isHidden ? 'block' : 'none';
    elements.btnToggleManualPaste.textContent = isHidden ? 'Скрыть поле ввода 📋' : 'Вставить отчет вручную 📋';
  });
}

if (elements.btnParseManualReport) {
  elements.btnParseManualReport.addEventListener('click', async () => {
    const rawText = elements.manualReportText.value.trim();
    if (!rawText) {
      log("Текст отчета не введен!", "warn");
      return;
    }

    elements.btnParseManualReport.disabled = true;
    elements.btnParseManualReport.textContent = "⏳ Анализ отчета...";
    log("Парсинг предоставленного диагностического отчета...", "info");

    try {
      const result = await apiDetectManual(rawText);
      if (result.success && result.data) {
        state.detectionData = result.data;
        displayDetectionResult(result.data);
        log(`Успешно распознан отчет: ${result.data.vendor} ${result.data.controller || ''} (FID: ${result.data.flash_id || '—'})`, "success");
        elements.btnProceedToFw.disabled = false;
        markSteps();
        elements.manualPasteContainer.style.display = 'none';
        elements.btnToggleManualPaste.textContent = 'Вставить отчет вручную 📋';
      } else {
        log(`Ошибка распознавания отчета: ${result.message}`, "warn");
      }
    } catch (err) {
      log(`Ошибка отправки отчета: ${err.message}`, "err");
    } finally {
      elements.btnParseManualReport.disabled = false;
      elements.btnParseManualReport.textContent = "🔍 Распознать и применить отчет";
    }
  });
}

elements.btnProceedToFw.addEventListener('click', () => {
  goToStep(3);
  loadFirmwares();
});

if (elements.btnProceedManualFw) {
  elements.btnProceedManualFw.addEventListener('click', () => {
    if (!state.detectionData) {
      state.detectionData = {
        vendor: "Phison / SMI / Maxio",
        controller: state.selectedDisk ? state.selectedDisk.name : "",
        flash_id: "",
        flash_desc: "",
        fw_version: state.selectedDisk ? state.selectedDisk.firmware : "",
        manual_override: true
      };
    }
    goToStep(3);
    loadFirmwares();
  });
}

elements.btnBackToStep2.addEventListener('click', () => goToStep(2));

elements.fwSearchInput.addEventListener('input', (e) => {
  const q = e.target.value.toLowerCase().trim();
  if (!q) {
    state.filteredFirmwares = [...state.firmwares];
  } else {
    state.filteredFirmwares = state.firmwares.filter(f => 
      f.filename.toLowerCase().includes(q) || 
      (f.target_nand && f.target_nand.toLowerCase().includes(q)) ||
      (f.generation && f.generation.toLowerCase().includes(q))
    );
  }
  renderFirmwares();
});

elements.btnProceedToFlash.addEventListener('click', () => {
  if (state.selectedDisk) {
    elements.summaryTargetDisk.textContent = `Диск ${state.selectedDisk.number}: ${state.selectedDisk.name}`;
    elements.summaryBusType.textContent = `Шина: ${state.selectedDisk.bus_type} (${state.selectedDisk.size_formatted})`;
  }
  if (state.selectedFirmware) {
    const fw = state.selectedFirmware;
    elements.summarySelectedFw.textContent = fw.filename;
    elements.summaryFwNand.textContent = fw.target_nand;

    const methodEl = document.getElementById('summaryMethod');
    const localPhison = fw.vendor === 'Phison' && fw.is_local;
    if (elements.headerPickRow) {
      elements.headerPickRow.style.display = localPhison ? 'flex' : 'none';
    }
    if (elements.selHeaderType) {
      elements.selHeaderType.value = fw.header_type || '';
    }
    elements.btnBuildAndFlash.disabled = !!(localPhison && fw.size_supported === false);

    if (fw.vendor === 'Maxio') {
      if (methodEl) methodEl.textContent = 'Локальный пакет Maxio MPTool';
      elements.btnBuildAndFlash.textContent = '🚀 Подготовить локальный Maxio MPTool';
    } else if (fw.vendor === 'Silicon Motion') {
      if (methodEl) methodEl.textContent = 'Локальный пакет Silicon Motion MPTool';
      elements.btnBuildAndFlash.textContent = '🚀 Подготовить локальный SMI MPTool';
    } else {
      if (methodEl) methodEl.textContent = 'Локальная сборка Phison S11 (fw.exe)';
      elements.btnBuildAndFlash.textContent = '🚀 Собрать и запустить fw.exe';
    }
  }
  goToStep(4);
});

elements.btnBackToStep3.addEventListener('click', () => goToStep(3));
elements.btnBuildAndFlash.addEventListener('click', buildAndLaunchFlasher);
elements.btnClearLog.addEventListener('click', () => {
  elements.terminalLog.innerHTML = '';
});

function boot() {
  if (state.booted) return;
  state.booted = true;
  markSteps();
  if (!desktopApi() && location.protocol !== 'http:' && location.protocol !== 'https:') {
    elements.diskListGrid.innerHTML = `
      <div style="padding: 24px; color: var(--text-muted); text-align: center; grid-column: 1/-1;">
        Интерфейс открыт как файл. Запустите SSD_Firmware_Studio.exe.
      </div>`;
    log("Нет связи с программой. Запустите SSD_Firmware_Studio.exe.", "warn");
    return;
  }
  loadDisks();
}

window.addEventListener('pywebviewready', boot);
window.addEventListener('DOMContentLoaded', () => {
  if (location.protocol === 'http:' || location.protocol === 'https:') boot();
});
