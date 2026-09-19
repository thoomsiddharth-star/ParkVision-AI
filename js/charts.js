/**
 * ParkVision AI - Operator Dashboard Analytics Charts
 * Powered by Chart.js
 */

class DashboardCharts {
  constructor() {
    this.occupancyChart = null;
    this.zonesChart = null;
    this.availabilityTrendChart = null;
    this.historyLabels = [];
    this.historyAvailableData = [];
  }

  init() {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js not yet loaded, retrying...');
      setTimeout(() => this.init(), 300);
      return;
    }

    this.initOccupancyChart();
    this.initZonesChart();
    this.initAvailabilityTrendChart();

    // Subscribe to live parkingService updates to update trend chart dynamically
    if (window.parkingService) {
      window.parkingService.subscribe((eventType, data) => {
        if (eventType === 'spaces_updated') {
          this.updateLiveTrend(data.stats);
        }
      });
    }
  }

  initOccupancyChart() {
    const ctx = document.getElementById('hourlyOccupancyChart');
    if (!ctx) return;

    const hourlyData = window.parkingService ? window.parkingService.analytics.hourlyOccupancy : [];
    const labels = hourlyData.map(d => d.hour);
    const occupancyVals = hourlyData.map(d => d.occupancy);

    this.occupancyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Occupancy Rate (%)',
          data: occupancyVals,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          borderWidth: 2.5,
          tension: 0.35,
          fill: true,
          pointBackgroundColor: '#2563eb',
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            titleFont: { family: 'Inter', size: 12 },
            bodyFont: { family: 'Inter', size: 12 },
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (item) => ` Occupancy: ${item.formattedValue}%`
            }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            ticks: {
              callback: (val) => `${val}%`,
              stepSize: 20,
              font: { family: 'Inter', size: 11 },
              color: '#64748b'
            },
            grid: { color: 'rgba(226, 232, 240, 0.7)' }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 11 },
              color: '#64748b'
            },
            grid: { display: false }
          }
        }
      }
    });
  }

  initZonesChart() {
    const ctx = document.getElementById('zonesBreakdownChart');
    if (!ctx) return;

    const zonesData = window.parkingService ? window.parkingService.analytics.zonesBreakdown : [];
    const labels = zonesData.map(z => z.zone);
    const occupiedVals = zonesData.map(z => z.occupied);
    const availableVals = zonesData.map(z => z.total - z.occupied);

    this.zonesChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Occupied',
            data: occupiedVals,
            backgroundColor: '#ef4444',
            borderRadius: 6
          },
          {
            label: 'Available',
            data: availableVals,
            backgroundColor: '#10b981',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 12,
              font: { family: 'Inter', size: 12 },
              color: '#334155'
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            stacked: true,
            ticks: { font: { family: 'Inter', size: 11 }, color: '#64748b' },
            grid: { display: false }
          },
          y: {
            stacked: true,
            max: 10,
            ticks: { stepSize: 2, font: { family: 'Inter', size: 11 }, color: '#64748b' },
            grid: { color: 'rgba(226, 232, 240, 0.7)' }
          }
        }
      }
    });
  }

  initAvailabilityTrendChart() {
    const ctx = document.getElementById('availabilityTrendChart');
    if (!ctx) return;

    // Initialize 6 data points backwards
    const now = new Date();
    for (let i = 5; i >= 0; i--) {
      const t = new Date(now.getTime() - i * 5000);
      this.historyLabels.push(`${t.getHours().toString().padStart(2, '0')}:${t.getMinutes().toString().padStart(2, '0')}:${t.getSeconds().toString().padStart(2, '0')}`);
      // fluctuate around 12 available
      this.historyAvailableData.push(11 + (i % 3));
    }

    this.availabilityTrendChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.historyLabels,
        datasets: [{
          label: 'Live Available Spaces',
          data: this.historyAvailableData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          borderWidth: 2.5,
          tension: 0.3,
          fill: true,
          pointBackgroundColor: '#10b981',
          pointRadius: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 8,
            cornerRadius: 6
          }
        },
        scales: {
          y: {
            min: 0,
            max: 20,
            ticks: { font: { family: 'Inter', size: 11 }, color: '#64748b', stepSize: 4 },
            grid: { color: 'rgba(226, 232, 240, 0.7)' }
          },
          x: {
            ticks: { font: { family: 'Inter', size: 10 }, color: '#64748b' },
            grid: { display: false }
          }
        }
      }
    });
  }

  updateLiveTrend(stats) {
    if (!this.availabilityTrendChart) return;

    const now = new Date();
    const timeLabel = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    this.historyLabels.push(timeLabel);
    this.historyAvailableData.push(stats.available);

    if (this.historyLabels.length > 10) {
      this.historyLabels.shift();
      this.historyAvailableData.shift();
    }

    this.availabilityTrendChart.update('none');
  }
}

window.DashboardCharts = DashboardCharts;
