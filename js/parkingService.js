/**
 * ParkVision AI - Data and Service Layer
 * 
 * Structured to cleanly decouple UI and data state.
 * Currently runs high-fidelity simulated real-time data (DEMO MODE).
 * Designed for immediate drop-in replacement with a real Python FastAPI + YOLO/OpenCV backend.
 */

class ParkingService {
  constructor() {
    this.isDemoMode = true; // Honesty requirement: clearly flags simulated state
    this.listeners = new Set();
    this.simulationInterval = null;
    this.simulationSpeedMs = 4500;
    this.selectedSpaceId = null;
    this.lastUpdated = new Date();

    // Initial 40 parking bays with exactly 12 available and 28 occupied (70% occupancy)
    // A01 AVAILABLE, A02 OCCUPIED, A03 AVAILABLE, A04 OCCUPIED, A05 AVAILABLE, A06 OCCUPIED, etc.
    this.spaces = this.initSpaces();

    // Nearby facilities demo data
    this.locations = [
      {
        id: 'central-hub',
        name: 'Central Parking Hub',
        address: '450 Innovation Way, Downtown',
        distance: '2.4 km',
        distanceMeters: 2400,
        estimatedTime: '8 min',
        totalSpaces: 40,
        availableSpaces: 12,
        occupiedSpaces: 28,
        occupancyRate: 70,
        status: 'Active',
        rate: '$4.50 / hr',
        cctvStatus: 'Online (4 Cameras)',
        lat: 37.7749,
        lng: -122.4194,
        zones: ['Zone A (Ground)', 'Zone B (Level 1)']
      },
      {
        id: 'city-center',
        name: 'City Center Parking',
        address: '120 Market St, Financial Plaza',
        distance: '3.1 km',
        distanceMeters: 3100,
        estimatedTime: '11 min',
        totalSpaces: 42,
        availableSpaces: 8,
        occupiedSpaces: 34,
        occupancyRate: 81,
        status: 'High Demand',
        rate: '$5.00 / hr',
        cctvStatus: 'Online (3 Cameras)',
        lat: 37.7833,
        lng: -122.4167,
        zones: ['Zone A (Main)']
      },
      {
        id: 'tech-park',
        name: 'Tech Park Parking',
        address: '88 Silicon Boulevard, Tech District',
        distance: '4.7 km',
        distanceMeters: 4700,
        estimatedTime: '14 min',
        totalSpaces: 40,
        availableSpaces: 21,
        occupiedSpaces: 19,
        occupancyRate: 48,
        status: 'Plenty Available',
        rate: '$3.50 / hr',
        cctvStatus: 'Online (6 Cameras)',
        lat: 37.7892,
        lng: -122.4014,
        zones: ['North Deck', 'South Deck']
      },
      {
        id: 'metro-plaza',
        name: 'Metro Plaza Garage',
        address: '15 Transit Station Rd',
        distance: '1.2 km',
        distanceMeters: 1200,
        estimatedTime: '5 min',
        totalSpaces: 50,
        availableSpaces: 15,
        occupiedSpaces: 35,
        occupancyRate: 70,
        status: 'Active',
        rate: '$3.00 / hr',
        cctvStatus: 'Online (4 Cameras)',
        lat: 37.7690,
        lng: -122.4467,
        zones: ['Lower Level', 'Upper Deck']
      }
    ];

    // Historical analytics data for Operator Dashboard
    this.analytics = {
      hourlyOccupancy: [
        { hour: '06:00', occupancy: 18, available: 33 },
        { hour: '07:00', occupancy: 32, available: 27 },
        { hour: '08:00', occupancy: 54, available: 18 },
        { hour: '09:00', occupancy: 82, available: 7 },
        { hour: '10:00', occupancy: 88, available: 5 },
        { hour: '11:00', occupancy: 78, available: 9 },
        { hour: '12:00', occupancy: 85, available: 6 },
        { hour: '13:00', occupancy: 72, available: 11 },
        { hour: '14:00', occupancy: 70, available: 12 },
        { hour: '15:00', occupancy: 75, available: 10 },
        { hour: '16:00', occupancy: 82, available: 7 },
        { hour: '17:00', occupancy: 90, available: 4 },
        { hour: '18:00', occupancy: 80, available: 8 }
      ],
      zonesBreakdown: [
        { zone: 'Zone A (North)', total: 10, occupied: 7, occupancy: 70 },
        { zone: 'Zone B (East)', total: 10, occupied: 8, occupancy: 80 },
        { zone: 'Zone C (South)', total: 10, occupied: 6, occupancy: 60 },
        { zone: 'Zone D (West)', total: 10, occupied: 7, occupancy: 70 }
      ],
      kpis: {
        totalSpaces: 40,
        peakOccupancy: '92%',
        avgOccupancy: '68%',
        dailyTurnover: '142 vehicles',
        avgParkDuration: '1h 45m',
        detectionAccuracy: '96.4%'
      }
    };

    // Activity log stream for operator
    this.activityLogs = [
      { id: 1, time: 'Just now', spaceId: 'A04', action: 'Occupied', vehicle: 'White Sedan (Conf: 97%)' },
      { id: 2, time: '1 min ago', spaceId: 'A11', action: 'Vacated', vehicle: 'Space cleared' },
      { id: 3, time: '3 min ago', spaceId: 'A28', action: 'Occupied', vehicle: 'Dark SUV (Conf: 95%)' },
      { id: 4, time: '5 min ago', spaceId: 'A09', action: 'Vacated', vehicle: 'Space cleared' },
      { id: 5, time: '7 min ago', spaceId: 'A18', action: 'Occupied', vehicle: 'Silver Hatchback (Conf: 96%)' }
    ];

    // Start real-time background simulation automatically
    this.startSimulation();
  }

  initSpaces() {
    const spaces = [];
    // 12 available spaces out of 40 = 28 occupied (70% occupancy)
    // Matches prompt requirement: A01 AVAILABLE, A02 OCCUPIED, A03 AVAILABLE, etc.
    const availableIndices = new Set([1, 3, 5, 7, 9, 13, 17, 21, 25, 29, 33, 37]); // exactly 12 items
    
    for (let i = 1; i <= 40; i++) {
      const idStr = 'A' + (i < 10 ? '0' + i : i);
      let status = availableIndices.has(i) ? 'AVAILABLE' : 'OCCUPIED';
      
      // Let one space be 'UNCERTAIN' for realism as per prompt section 4 ("A06 UNCERTAIN")
      if (i === 6) {
        status = 'UNCERTAIN';
      }

      const zone = i <= 10 ? 'Ground Floor (North)' : 
                   i <= 20 ? 'Ground Floor (East)' : 
                   i <= 30 ? 'Ground Floor (South)' : 'Ground Floor (West)';

      spaces.push({
        id: idStr,
        number: i,
        status: status, // 'AVAILABLE' | 'OCCUPIED' | 'UNCERTAIN'
        zone: zone,
        vehicleType: status === 'OCCUPIED' ? (i % 2 === 0 ? 'SUV' : 'Sedan') : null,
        confidence: status === 'OCCUPIED' ? Math.floor(92 + Math.random() * 6) : (status === 'UNCERTAIN' ? 68 : null),
        lastUpdated: 'Just now'
      });
    }
    return spaces;
  }

  getStats() {
    const total = this.spaces.length;
    const available = this.spaces.filter(s => s.status === 'AVAILABLE').length;
    const occupied = this.spaces.filter(s => s.status === 'OCCUPIED').length;
    const uncertain = this.spaces.filter(s => s.status === 'UNCERTAIN').length;
    const occupancyRate = Math.round(((occupied) / total) * 100);

    return {
      total,
      available,
      occupied,
      uncertain,
      occupancyRate,
      lastUpdatedText: this.getRelativeTime(this.lastUpdated)
    };
  }

  getSpaces() {
    return [...this.spaces];
  }

  getSpaceById(id) {
    return this.spaces.find(s => s.id === id);
  }

  getLocations() {
    // Keep Central Parking Hub in sync with live spaces count
    const stats = this.getStats();
    this.locations[0].availableSpaces = stats.available;
    this.locations[0].occupiedSpaces = stats.occupied;
    this.locations[0].occupancyRate = stats.occupancyRate;
    return [...this.locations];
  }

  getLocationById(id) {
    return this.locations.find(l => l.id === id) || this.locations[0];
  }

  selectSpace(spaceId) {
    const space = this.getSpaceById(spaceId);
    if (!space) return { success: false, message: 'Space not found' };

    if (space.status === 'OCCUPIED') {
      return {
        success: false,
        status: 'OCCUPIED',
        spaceId: space.id,
        message: `Space ${space.id} is currently occupied.`,
        suggestion: 'View available spaces'
      };
    }

    this.selectedSpaceId = spaceId;
    this.notifyListeners('space_selected', { spaceId, space });
    return {
      success: true,
      status: space.status,
      spaceId: space.id,
      message: `Parking space ${space.id} selected.`,
      space
    };
  }

  getSelectedSpace() {
    return this.selectedSpaceId ? this.getSpaceById(this.selectedSpaceId) : null;
  }

  startSimulation() {
    if (this.simulationInterval) return;
    this.simulationInterval = setInterval(() => {
      this.triggerRandomChange();
    }, this.simulationSpeedMs);
  }

  stopSimulation() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = null;
    }
  }

  isSimulationRunning() {
    return this.simulationInterval !== null;
  }

  triggerRandomChange() {
    // Pick 1 to 2 random spaces to toggle to simulate realistic vehicle entry/exit
    const countToChange = Math.random() > 0.4 ? 1 : 2;
    const changedSpaces = [];

    for (let i = 0; i < countToChange; i++) {
      const randIndex = Math.floor(Math.random() * this.spaces.length);
      const space = this.spaces[randIndex];
      const oldStatus = space.status;

      let newStatus = oldStatus;
      if (oldStatus === 'AVAILABLE') {
        newStatus = 'OCCUPIED';
        space.confidence = Math.floor(92 + Math.random() * 7);
        space.vehicleType = Math.random() > 0.5 ? 'SUV' : 'Sedan';
        this.addLog(space.id, 'Occupied', `${space.vehicleType} detected (${space.confidence}%)`);
      } else if (oldStatus === 'OCCUPIED') {
        newStatus = 'AVAILABLE';
        space.confidence = null;
        space.vehicleType = null;
        this.addLog(space.id, 'Vacated', 'Vehicle departed, space clear');
      } else {
        // UNCERTAIN resolves
        newStatus = Math.random() > 0.5 ? 'AVAILABLE' : 'OCCUPIED';
        space.confidence = 94;
      }

      space.status = newStatus;
      space.lastUpdated = 'Just now';
      changedSpaces.push({ space, oldStatus, newStatus });
    }

    this.lastUpdated = new Date();
    this.notifyListeners('spaces_updated', { changedSpaces, stats: this.getStats() });
  }

  addLog(spaceId, action, details) {
    this.activityLogs.unshift({
      id: Date.now() + Math.random(),
      time: 'Just now',
      spaceId,
      action,
      vehicle: details
    });
    if (this.activityLogs.length > 20) {
      this.activityLogs.pop();
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notifyListeners(eventType, payload) {
    this.listeners.forEach(fn => {
      try {
        fn(eventType, payload);
      } catch (err) {
        console.error('Listener callback error:', err);
      }
    });
  }

  getRelativeTime(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 5) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    return '1 min ago';
  }
}

// Global singleton instance
window.parkingService = new ParkingService();
