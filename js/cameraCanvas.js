/**
 * ParkVision AI - Interactive AI CCTV Camera & Computer Vision Simulator
 * 
 * Renders a high-fidelity top-down/isometric smart parking lot CCTV feed
 * with real-time YOLO bounding box overlays, confidence metrics, and scanlines.
 * 
 * Honest Disclosure: Clearly labeled "DEMO MODE — Simulated real-time detection"
 */

class CameraSimulator {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.activeCamera = 'CAM-01'; // 'CAM-01' | 'CAM-02'
    this.showBoundingBoxes = true;
    this.showConfidence = true;
    this.showScanline = true;
    this.scanlineY = 0;
    this.scanDirection = 1;
    this.animFrameId = null;
    this.lastTime = performance.now();
    this.fps = 30;
    this.confidenceScore = 96;
    
    // Set internal resolution
    this.width = 1280;
    this.height = 720;
    this.canvas.width = this.width;
    this.canvas.height = this.height;

    // Listen to parkingService changes to keep bay statuses synchronized
    if (window.parkingService) {
      window.parkingService.subscribe((eventType, data) => {
        if (eventType === 'spaces_updated') {
          // Slight fluctuation in confidence for realism
          this.confidenceScore = Math.floor(94 + Math.random() * 5);
          const confEl = document.getElementById('ai-cam-confidence');
          if (confEl) confEl.textContent = `${this.confidenceScore}%`;
        }
      });
    }

    this.startLoop();
  }

  setCamera(camId) {
    this.activeCamera = camId;
  }

  toggleBoundingBoxes(enabled) {
    this.showBoundingBoxes = enabled;
  }

  toggleConfidence(enabled) {
    this.showConfidence = enabled;
  }

  toggleScanline(enabled) {
    this.showScanline = enabled;
  }

  startLoop() {
    const render = (time) => {
      const delta = time - this.lastTime;
      this.lastTime = time;
      this.fps = Math.round(1000 / (delta || 33));

      this.update(delta);
      this.draw();

      this.animFrameId = requestAnimationFrame(render);
    };
    this.animFrameId = requestAnimationFrame(render);
  }

  stopLoop() {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }

  update(delta) {
    // Scanline animation
    if (this.showScanline) {
      this.scanlineY += this.scanDirection * (delta * 0.18);
      if (this.scanlineY > this.height) {
        this.scanlineY = 0;
      }
    }
  }

  draw() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    ctx.clearRect(0, 0, w, h);

    // 1. Asphalt Background
    ctx.fillStyle = '#1e2530';
    ctx.fillRect(0, 0, w, h);

    // Subtle road texture grain
    ctx.fillStyle = 'rgba(255, 255, 255, 0.015)';
    for (let i = 0; i < 40; i++) {
      ctx.fillRect((i * 123) % w, (i * 97) % h, 4, 4);
    }

    // 2. Driveways and Lanes
    this.drawDriveways(ctx, w, h);

    // 3. Draw Parking Bays according to active camera
    this.drawParkingBays(ctx, w, h);

    // 4. Moving / Animated Scanline
    if (this.showScanline) {
      this.drawScanline(ctx, w, h);
    }

    // 5. CCTV Camera HUD & Telemetry
    this.drawCCTVOverlay(ctx, w, h);
  }

  drawDriveways(ctx, w, h) {
    // Central lane
    ctx.fillStyle = '#151b24';
    ctx.fillRect(0, 240, w, 240);

    // Directional arrows and lane lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 4;
    ctx.setLineDash([20, 20]);
    ctx.beginPath();
    ctx.moveTo(0, 360);
    ctx.lineTo(w, 360);
    ctx.stroke();
    ctx.setLineDash([]);

    // Lane arrows
    this.drawArrow(ctx, 220, 310, 'right');
    this.drawArrow(ctx, 640, 310, 'right');
    this.drawArrow(ctx, 1060, 310, 'right');

    this.drawArrow(ctx, 220, 410, 'left');
    this.drawArrow(ctx, 640, 410, 'left');
    this.drawArrow(ctx, 1060, 410, 'left');
  }

  drawArrow(ctx, x, y, dir) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.beginPath();
    if (dir === 'right') {
      ctx.moveTo(x - 25, y - 8);
      ctx.lineTo(x + 10, y - 8);
      ctx.lineTo(x + 10, y - 18);
      ctx.lineTo(x + 30, y);
      ctx.lineTo(x + 10, y + 18);
      ctx.lineTo(x + 10, y + 8);
      ctx.lineTo(x - 25, y + 8);
    } else {
      ctx.moveTo(x + 25, y - 8);
      ctx.lineTo(x - 10, y - 8);
      ctx.lineTo(x - 10, y - 18);
      ctx.lineTo(x - 30, y);
      ctx.lineTo(x - 10, y + 18);
      ctx.lineTo(x - 10, y + 8);
      ctx.lineTo(x + 25, y + 8);
    }
    ctx.closePath();
    ctx.fill();
  }

  drawParkingBays(ctx, w, h) {
    const spaces = window.parkingService ? window.parkingService.getSpaces() : [];
    
    // CAM-01 focuses on North / Top row (A01 - A10) and South / Bottom row (A11 - A20)
    // CAM-02 focuses on A21 - A30 and A31 - A40
    const offset = this.activeCamera === 'CAM-01' ? 0 : 20;

    const topSpaces = spaces.slice(offset, offset + 10);
    const bottomSpaces = spaces.slice(offset + 10, offset + 20);

    const bayWidth = 105;
    const bayHeight = 180;
    const startX = 65;
    const gap = 15;

    // Draw Top Row (facing down)
    topSpaces.forEach((space, idx) => {
      const x = startX + idx * (bayWidth + gap);
      const y = 40;
      this.drawBay(ctx, space, x, y, bayWidth, bayHeight, 'top');
    });

    // Draw Bottom Row (facing up)
    bottomSpaces.forEach((space, idx) => {
      const x = startX + idx * (bayWidth + gap);
      const y = 500;
      this.drawBay(ctx, space, x, y, bayWidth, bayHeight, 'bottom');
    });
  }

  drawBay(ctx, space, x, y, width, height, orientation) {
    const isOccupied = space.status === 'OCCUPIED';
    const isUncertain = space.status === 'UNCERTAIN';

    // Bay lines (white markings on asphalt)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, y + height);
    ctx.moveTo(x + width, y);
    ctx.lineTo(x + width, y + height);
    if (orientation === 'top') {
      ctx.moveTo(x, y);
      ctx.lineTo(x + width, y);
    } else {
      ctx.moveTo(x, y + height);
      ctx.lineTo(x + width, y + height);
    }
    ctx.stroke();

    // Bay ID on pavement
    ctx.font = '600 13px "JetBrains Mono", monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.textAlign = 'center';
    const textY = orientation === 'top' ? y + 25 : y + height - 15;
    ctx.fillText(space.id, x + width / 2, textY);

    // If occupied, draw realistic car
    if (isOccupied) {
      this.drawCar(ctx, x + 12, y + 20, width - 24, height - 40, space.id, orientation);
    }

    // Overlay YOLO Bounding Box & Status Badge
    if (this.showBoundingBoxes) {
      this.drawYoloBoundingBox(ctx, space, x - 3, y - 3, width + 6, height + 6, orientation);
    }
  }

  drawCar(ctx, x, y, w, h, id, orientation) {
    // Car color determinism by id
    const colors = [
      { body: '#e2e8f0', roof: '#cbd5e1', window: '#1e293b' }, // Silver
      { body: '#1e293b', roof: '#0f172a', window: '#090d16' }, // Black
      { body: '#2563eb', roof: '#1d4ed8', window: '#0f172a' }, // Deep Blue
      { body: '#dc2626', roof: '#b91c1c', window: '#1e293b' }, // Crimson
      { body: '#f8fafc', roof: '#e2e8f0', window: '#334155' }  // White
    ];
    const colorIndex = parseInt(id.replace(/\D/g, ''), 10) % colors.length;
    const c = colors[colorIndex];

    ctx.save();
    // Shadow under car
    ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
    ctx.beginPath();
    ctx.roundRect(x - 2, y + 2, w + 4, h + 4, 10);
    ctx.fill();

    // Car Body
    ctx.fillStyle = c.body;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 8);
    ctx.fill();

    // Windshield & Rear Window
    ctx.fillStyle = c.window;
    if (orientation === 'top') {
      // Front windshield (facing down)
      ctx.beginPath();
      ctx.roundRect(x + 6, y + h - 45, w - 12, 16, 3);
      ctx.fill();
      // Rear windshield (top)
      ctx.beginPath();
      ctx.roundRect(x + 8, y + 16, w - 16, 12, 3);
      ctx.fill();
      // Roof
      ctx.fillStyle = c.roof;
      ctx.beginPath();
      ctx.roundRect(x + 7, y + 32, w - 14, h - 80, 4);
      ctx.fill();
      // Headlights (facing down)
      ctx.fillStyle = '#fef08a';
      ctx.fillRect(x + 4, y + h - 5, 8, 4);
      ctx.fillRect(x + w - 12, y + h - 5, 8, 4);
    } else {
      // Front windshield (facing up)
      ctx.beginPath();
      ctx.roundRect(x + 6, y + 28, w - 12, 16, 3);
      ctx.fill();
      // Rear windshield
      ctx.beginPath();
      ctx.roundRect(x + 8, y + h - 28, w - 16, 12, 3);
      ctx.fill();
      // Roof
      ctx.fillStyle = c.roof;
      ctx.beginPath();
      ctx.roundRect(x + 7, y + 48, w - 14, h - 80, 4);
      ctx.fill();
      // Headlights (facing up)
      ctx.fillStyle = '#fef08a';
      ctx.fillRect(x + 4, y + 1, 8, 4);
      ctx.fillRect(x + w - 12, y + 1, 8, 4);
    }
    ctx.restore();
  }

  drawYoloBoundingBox(ctx, space, x, y, w, h, orientation) {
    ctx.save();
    let borderColor = '#10b981'; // green for available
    let tagText = `${space.id} → AVAILABLE`;
    let bgColor = 'rgba(16, 185, 129, 0.12)';

    if (space.status === 'OCCUPIED') {
      borderColor = '#ef4444'; // red for occupied
      const conf = space.confidence || 96;
      tagText = this.showConfidence 
        ? `${space.id} → OCCUPIED [${conf}%]` 
        : `${space.id} → OCCUPIED`;
      bgColor = 'rgba(239, 68, 68, 0.14)';
    } else if (space.status === 'UNCERTAIN') {
      borderColor = '#f59e0b';
      tagText = `${space.id} → UNCERTAIN`;
      bgColor = 'rgba(245, 158, 11, 0.14)';
    }

    // Box highlight
    ctx.fillStyle = bgColor;
    ctx.fillRect(x, y, w, h);

    // Box stroke
    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 1.8;
    ctx.strokeRect(x, y, w, h);

    // High-tech corner accents (YOLO visual marker style)
    const cornerLen = 10;
    ctx.lineWidth = 3;
    // Top-left
    ctx.beginPath();
    ctx.moveTo(x, y + cornerLen);
    ctx.lineTo(x, y);
    ctx.lineTo(x + cornerLen, y);
    ctx.stroke();
    // Top-right
    ctx.beginPath();
    ctx.moveTo(x + w - cornerLen, y);
    ctx.lineTo(x + w, y);
    ctx.lineTo(x + w, y + cornerLen);
    ctx.stroke();
    // Bottom-left
    ctx.beginPath();
    ctx.moveTo(x, y + h - cornerLen);
    ctx.lineTo(x, y + h);
    ctx.lineTo(x + cornerLen, y + h);
    ctx.stroke();
    // Bottom-right
    ctx.beginPath();
    ctx.moveTo(x + w - cornerLen, y + h);
    ctx.lineTo(x + w, y + h);
    ctx.lineTo(x + w, y + h - cornerLen);
    ctx.stroke();

    // Floating YOLO tag badge
    ctx.font = '600 10px "JetBrains Mono", monospace';
    const textWidth = ctx.measureText(tagText).width;
    const badgeHeight = 18;
    const badgeY = orientation === 'top' ? y - badgeHeight : y + h;

    ctx.fillStyle = borderColor;
    ctx.fillRect(x, badgeY, textWidth + 12, badgeHeight);

    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'left';
    ctx.fillText(tagText, x + 6, badgeY + 13);

    ctx.restore();
  }

  drawScanline(ctx, w, h) {
    const grad = ctx.createLinearGradient(0, this.scanlineY - 20, 0, this.scanlineY + 20);
    grad.addColorStop(0, 'rgba(59, 130, 246, 0)');
    grad.addColorStop(0.5, 'rgba(59, 130, 246, 0.35)');
    grad.addColorStop(1, 'rgba(59, 130, 246, 0)');

    ctx.fillStyle = grad;
    ctx.fillRect(0, this.scanlineY - 20, w, 40);

    // Crisp laser beam in center of scanline
    ctx.fillStyle = 'rgba(96, 165, 250, 0.85)';
    ctx.fillRect(0, this.scanlineY, w, 2);
  }

  drawCCTVOverlay(ctx, w, h) {
    ctx.save();
    // Top Left: Camera ID, stream, resolution
    ctx.font = '600 13px "JetBrains Mono", monospace';
    ctx.fillStyle = '#38bdf8';
    ctx.textAlign = 'left';
    ctx.fillText(`● REC [${this.activeCamera}] - NORTH GROUND DECK`, 24, 30);

    ctx.font = '400 11px "JetBrains Mono", monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fillText(`RTSP://192.168.1.104:554/live | 1920x1080 | H.264`, 24, 48);

    // Top Right: Live timestamp & FPS
    const now = new Date();
    const timeStr = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    ctx.textAlign = 'right';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(timeStr, w - 24, 30);

    ctx.fillStyle = '#4ade80';
    ctx.fillText(`FPS: ${this.fps}  |  LATENCY: 14ms`, w - 24, 48);

    // Bottom Center: Demo Mode Honest Disclosure Overlay
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    const bannerWidth = 420;
    ctx.fillRect((w - bannerWidth) / 2, h - 38, bannerWidth, 26);
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 1;
    ctx.strokeRect((w - bannerWidth) / 2, h - 38, bannerWidth, 26);

    ctx.fillStyle = '#fef08a';
    ctx.font = '600 11px "Inter", sans-serif';
    ctx.fillText('DEMO MODE — Simulated real-time detection (YOLOv8 CV)', w / 2, h - 21);

    ctx.restore();
  }
}

window.CameraSimulator = CameraSimulator;
