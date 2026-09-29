'use strict';
const observations = JSON.parse(document.getElementById('rainfall-data').textContent);
const byDate = new Map(observations.map(row => [row.date, row]));
const marks = [...document.querySelectorAll('.day-mark')];
const rows = [...document.querySelectorAll('.month-row')];
const scaleButtons = [...document.querySelectorAll('[data-scale]')];
const monthSelect = document.getElementById('month');
const dateText = document.getElementById('selected-date');
const valueText = document.getElementById('selected-value');
const noteText = document.getElementById('selected-note');
const maxReading = observations.filter(row => row.mm !== null).reduce((a, b) => a.mm > b.mm ? a : b);
const dateFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'long', year: 'numeric', timeZone: 'UTC' });
let selectedDate = maxReading.date;

function selectDay(mark, moveFocus = false) {
  const reading = byDate.get(mark.dataset.date);
  selectedDate = reading.date;
  const readingMonth = Number(reading.date.slice(5, 7));
  if (monthSelect.value !== '0' && Number(monthSelect.value) !== readingMonth) {
    monthSelect.value = String(readingMonth);
    for (const row of rows) row.classList.toggle('dimmed', Number(row.dataset.month) !== readingMonth);
  }
  for (const item of marks) {
    const selected = item === mark;
    item.classList.toggle('selected', selected);
    item.setAttribute('aria-pressed', String(selected));
    item.setAttribute('tabindex', selected ? '0' : '-1');
  }
  dateText.textContent = dateFormat.format(new Date(`${reading.date}T12:00:00Z`)).toUpperCase();
  valueText.textContent = reading.kind === 'trace' ? 'Trace <0.05 mm' : `${reading.mm.toFixed(1)} mm`;
  noteText.textContent = reading.kind === 'trace' ? 'Observed rain; exact amount unquantified' :
    reading.mm === 0 ? 'No recorded rainfall' :
    reading.date === maxReading.date ? 'The wettest day of the year' : 'Daily total at Hong Kong Observatory';
  if (moveFocus) mark.focus({ preventScroll: true });
}

for (const mark of marks) {
  mark.addEventListener('click', () => selectDay(mark));
  mark.addEventListener('focus', () => selectDay(mark));
  mark.addEventListener('keydown', event => {
    const visible = monthSelect.value === '0' ? marks : marks.filter(item => Number(item.dataset.date.slice(5, 7)) === Number(monthSelect.value));
    const index = visible.indexOf(mark);
    let next;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = Math.min(visible.length - 1, index + 1);
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = Math.max(0, index - 1);
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = visible.length - 1;
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectDay(mark); }
    if (next !== undefined) { event.preventDefault(); selectDay(visible[next], true); visible[next].scrollIntoView({block:'nearest', inline:'nearest'}); }
  });
}

for (const button of scaleButtons) {
  button.addEventListener('click', () => {
    const squareRoot = button.dataset.scale === 'sqrt';
    for (const mark of marks) {
      const line = mark.querySelector('.rain');
      if (!line) continue;
      const fraction = Number(mark.dataset.value) / 400;
      const height = 47 * (squareRoot ? Math.sqrt(fraction) : fraction);
      line.setAttribute('y2', Number(mark.dataset.y) + height);
    }
    for (const other of scaleButtons) { other.classList.toggle('active', other === button); other.setAttribute('aria-pressed', String(other === button)); }
    document.getElementById('scale-note').textContent = squareRoot ?
      'Square-root length scale, shared by all months: four times the rain makes a stroke twice as long.' :
      'Linear length scale, shared by all months: twice the rain makes a stroke twice as long. Small amounts may appear very short.';
  });
}

monthSelect.addEventListener('change', () => {
  const month = Number(monthSelect.value);
  for (const row of rows) row.classList.toggle('dimmed', month !== 0 && Number(row.dataset.month) !== month);
  if (month !== 0 && Number(selectedDate.slice(5, 7)) !== month) {
    selectDay(marks.find(mark => Number(mark.dataset.date.slice(5, 7)) === month));
  }
});
for (const control of document.querySelectorAll('.controls,.readout,.chart-instruction')) control.hidden = false;
selectDay(marks.find(mark => mark.dataset.date === selectedDate));
