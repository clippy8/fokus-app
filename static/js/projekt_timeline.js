(function () {
    var timeline = document.getElementById('timeline');
    if (!timeline) return;

    var windowStart = new Date(timeline.dataset.windowStart + 'T00:00:00');
    var totalDays = parseInt(timeline.dataset.totalDays, 10);
    var pxPerDay = parseInt(timeline.dataset.pxPerDay, 10);
    var defaultDuration = parseInt(timeline.dataset.defaultDuration, 10);
    var rowsContainer = document.getElementById('timeline-rows');
    var trayContainer = document.getElementById('tray-items');
    var rowTemplate = document.getElementById('row-template');

    function getCookie(name) {
        var match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return match ? decodeURIComponent(match.pop()) : '';
    }
    var csrftoken = getCookie('csrftoken');

    function addDays(date, days) {
        var d = new Date(date);
        d.setDate(d.getDate() + days);
        return d;
    }

    function toIso(date) {
        var y = date.getFullYear();
        var m = String(date.getMonth() + 1).padStart(2, '0');
        var d = String(date.getDate()).padStart(2, '0');
        return y + '-' + m + '-' + d;
    }

    function dayOffsetToDate(offsetDays) {
        return toIso(addDays(windowStart, offsetDays));
    }

    function dateToDayOffset(iso) {
        var d = new Date(iso + 'T00:00:00');
        return Math.round((d - windowStart) / 86400000);
    }

    function clampOffset(offset) {
        return Math.max(0, Math.min(totalDays - 1, offset));
    }

    function persistDates(id, startIso, endIso) {
        fetch('/goals/projekte/' + id + '/update-dates/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'start_date=' + encodeURIComponent(startIso || '') + '&end_date=' + encodeURIComponent(endIso || ''),
        }).then(function (response) {
            if (!response.ok) {
                response.json().then(function (data) {
                    alert(data.error || 'Speichern fehlgeschlagen.');
                });
            }
        });
    }

    function positionBar(bar) {
        var startOffset = dateToDayOffset(bar.dataset.start);
        var endOffset = dateToDayOffset(bar.dataset.end);
        var duration = Math.max(1, endOffset - startOffset);
        bar.style.left = (startOffset * pxPerDay) + 'px';
        bar.style.width = (duration * pxPerDay) + 'px';
    }

    function updateManualInputs(row, startIso, endIso) {
        var startInput = row.querySelector('.manual-start');
        var endInput = row.querySelector('.manual-end');
        if (startInput) startInput.value = startIso || '';
        if (endInput) endInput.value = endIso || '';
    }

    // --- Whole-bar drag (reposition, same duration) ---
    var dragState = null;

    rowsContainer.addEventListener('dragstart', function (e) {
        var bar = e.target.closest('.timeline-bar');
        if (!bar) return;
        var track = bar.closest('.timeline-track');
        var trackRect = track.getBoundingClientRect();
        dragState = {
            type: 'move',
            bar: bar,
            grabOffsetPx: e.clientX - (trackRect.left + parseFloat(bar.style.left || 0)),
        };
        e.dataTransfer.setData('text/plain', bar.dataset.id);
        e.dataTransfer.effectAllowed = 'move';
    });

    rowsContainer.addEventListener('dragover', function (e) {
        e.preventDefault();
    });

    rowsContainer.addEventListener('drop', function (e) {
        e.preventDefault();
        if (dragState && dragState.type === 'move') {
            var bar = dragState.bar;
            var track = bar.closest('.timeline-track');
            var trackRect = track.getBoundingClientRect();
            var durationDays = Math.max(1, dateToDayOffset(bar.dataset.end) - dateToDayOffset(bar.dataset.start));
            var newLeftPx = e.clientX - trackRect.left - dragState.grabOffsetPx;
            var newStartOffset = clampOffset(Math.round(newLeftPx / pxPerDay));
            newStartOffset = Math.min(newStartOffset, totalDays - durationDays);
            newStartOffset = Math.max(0, newStartOffset);
            var newStartIso = dayOffsetToDate(newStartOffset);
            var newEndIso = dayOffsetToDate(newStartOffset + durationDays);
            bar.dataset.start = newStartIso;
            bar.dataset.end = newEndIso;
            positionBar(bar);
            updateManualInputs(bar.closest('.timeline-row'), newStartIso, newEndIso);
            persistDates(bar.dataset.id, newStartIso, newEndIso);
            dragState = null;
            return;
        }
        var trayId = e.dataTransfer.getData('text/tray-id');
        if (trayId) {
            scheduleFromTray(trayId, e.clientX);
        }
    });

    // --- Resize handles (independent start/end adjustment) ---
    var resizeState = null;

    rowsContainer.addEventListener('mousedown', function (e) {
        var handle = e.target.closest('.resize-handle');
        if (!handle) return;
        e.preventDefault();
        var bar = handle.closest('.timeline-bar');
        var side = handle.classList.contains('resize-left') ? 'left' : 'right';
        resizeState = {
            bar: bar,
            side: side,
            startOffset: dateToDayOffset(bar.dataset.start),
            endOffset: dateToDayOffset(bar.dataset.end),
            startX: e.clientX,
        };
    });

    document.addEventListener('mousemove', function (e) {
        if (!resizeState) return;
        var deltaDays = Math.round((e.clientX - resizeState.startX) / pxPerDay);
        var newStart = resizeState.startOffset;
        var newEnd = resizeState.endOffset;
        if (resizeState.side === 'left') {
            newStart = Math.min(resizeState.endOffset - 1, clampOffset(resizeState.startOffset + deltaDays));
        } else {
            newEnd = Math.max(resizeState.startOffset + 1, clampOffset(resizeState.endOffset + deltaDays));
        }
        resizeState.bar.dataset.start = dayOffsetToDate(newStart);
        resizeState.bar.dataset.end = dayOffsetToDate(newEnd);
        positionBar(resizeState.bar);
    });

    document.addEventListener('mouseup', function () {
        if (!resizeState) return;
        var bar = resizeState.bar;
        var startIso = bar.dataset.start;
        var endIso = bar.dataset.end;
        updateManualInputs(bar.closest('.timeline-row'), startIso, endIso);
        persistDates(bar.dataset.id, startIso, endIso);
        resizeState = null;
    });

    // --- Tray items (not yet scheduled projects) ---
    trayContainer.addEventListener('dragstart', function (e) {
        var item = e.target.closest('.tray-item');
        if (!item) return;
        e.dataTransfer.setData('text/tray-id', item.dataset.id);
        e.dataTransfer.effectAllowed = 'move';
    });

    function scheduleFromTray(id, clientX) {
        var item = trayContainer.querySelector('.tray-item[data-id="' + id + '"]');
        if (!item) return;
        var title = item.textContent;
        var rowsRect = rowsContainer.getBoundingClientRect();
        var startOffset = clampOffset(Math.round((clientX - rowsRect.left) / pxPerDay));
        startOffset = Math.min(startOffset, totalDays - defaultDuration);
        startOffset = Math.max(0, startOffset);
        var startIso = dayOffsetToDate(startOffset);
        var endIso = dayOffsetToDate(startOffset + defaultDuration);

        var fragment = rowTemplate.content.cloneNode(true);
        var row = fragment.querySelector('.timeline-row');
        row.dataset.rowId = id;
        row.querySelector('.row-title').textContent = title;
        var bar = row.querySelector('.timeline-bar');
        bar.dataset.id = id;
        bar.dataset.start = startIso;
        bar.dataset.end = endIso;
        row.querySelector('.bar-label').textContent = title;
        row.querySelector('.manual-dates').dataset.id = id;
        row.querySelector('.edit-link').setAttribute('href', '/goals/projekte/' + id + '/edit/');
        positionBar(bar);
        updateManualInputs(row, startIso, endIso);

        rowsContainer.appendChild(row);
        item.remove();
        if (!trayContainer.querySelector('.tray-item')) {
            trayContainer.innerHTML = '<p><small>Alle Projekte sind eingeplant.</small></p>';
        }
        persistDates(id, startIso, endIso);
    }

    // --- Manual Von/Bis inputs ---
    rowsContainer.addEventListener('change', function (e) {
        if (!e.target.classList.contains('manual-start') && !e.target.classList.contains('manual-end')) return;
        var row = e.target.closest('.timeline-row');
        var bar = row.querySelector('.timeline-bar');
        var startInput = row.querySelector('.manual-start');
        var endInput = row.querySelector('.manual-end');
        var startIso = startInput.value;
        var endIso = endInput.value;
        if (!startIso || !endIso) return;
        if (endIso < startIso) {
            alert('Das Bis-Datum muss nach dem Von-Datum liegen.');
            return;
        }
        bar.dataset.start = startIso;
        bar.dataset.end = endIso;
        positionBar(bar);
        persistDates(bar.dataset.id, startIso, endIso);
    });

    // Initial positioning (in case of rounding drift vs. server-rendered inline styles)
    rowsContainer.querySelectorAll('.timeline-bar').forEach(positionBar);
})();
