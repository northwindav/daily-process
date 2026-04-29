/**
 * GOES IR Looper - GIF Download Functionality
 * Creates and downloads animated GIF from looper's currently displayed images
 * Uses gif.js library (https://github.com/jnordberg/gif.js)
 */

class GOESIRGifDownloader {
  constructor() {
    // gif.js library should be loaded from CDN before this script
    this.isProcessing = false;
    this.animatorEl = document.getElementById('wxo-animator');
    
    // Configuration for file size optimization
    // Skip every Nth frame to reduce file size: 1=all frames, 2=every 2nd, 3=every 3rd, etc.
    this.frameSkip = 1;  // Default: keep all frames from the displayed range
    
    // Quality setting: lower = smaller file but lower quality
    // Range: 1-30, default 10. Use 2-5 for smaller files.
    this.gifQuality = 5;  // Default quality setting
    
    // Image resolution: pixel width for GIF frames
    // Options: 600 (tiny), 800 (small), 1000 (medium), 1200 (large)
    // PowerPoint: 600-800px is adequate for typical slides
    this.imageWidth = 1200;  // Full resolution for better quality
    
    // Frame delay in milliseconds: 100ms=10fps (smooth), 200ms=5fps (smaller files)
    this.frameDelayMs = 100;  // 100ms = 10 FPS animation speed
    
    // Enable dithering for better color compression
    this.ditherMode = 'FloydSteinberg';  // Options: false, 'FloydSteinberg', etc.
  }

  /**
   * Extract image URLs from wxo-animator data attributes
   * Returns array of {url, label} objects for CURRENTLY DISPLAYED images
   * Uses the from/to time selects to determine visible range
   * Applies frame skipping only within the displayed range
   */
  extractImageUrls() {
    // Get fresh element in case DOM changed
    const animator = document.getElementById('wxo-animator');
    
    if (!animator) {
      console.error('wxo-animator element not found');
      return [];
    }

    // Get the visible range from the time selects (set by fetch_goes_page.py configuration)
    const fromSelect = document.getElementById('wxo-anim-from-time');
    const toSelect = document.getElementById('wxo-anim-to-time');
    
    let fromIndex = 0;
    let toIndex = 294;  // Default to last image
    
    if (fromSelect && toSelect) {
      fromIndex = parseInt(fromSelect.value) || 0;
      toIndex = parseInt(toSelect.value) || 294;
    }
    
    const visibleFrameCount = toIndex - fromIndex + 1;
    console.log(`Browser displaying frames ${fromIndex}-${toIndex} (${visibleFrameCount} images in ~${(visibleFrameCount / 6).toFixed(1)} hours)`);

    const images = [];
    
    // Extract only images in the currently displayed range with frame skipping
    // Use getAttribute because dataset doesn't handle hyphens followed by numbers correctly
    for (let i = fromIndex; i <= toIndex; i += this.frameSkip) {
      const url = animator.getAttribute(`data-wxo-anim-${i}`);
      const label = animator.getAttribute(`data-wxo-label-${i}`);
      if (url) {
        images.push({ url, label });
      }
    }

    console.log(`Extracted ${images.length} images (from displayed range, with ${this.frameSkip}x frame skip)`);
    return images;
  }

  /**
   * Fetch an image and return as canvas
   */
  async fetchAndCanvasImage(url) {
    return new Promise((resolve, reject) => {
      // Use image proxy to avoid CORS issues with weather.gc.ca
      // The proxy fetches from weather.gc.ca and serves with CORS headers
      const proxyUrl = new URL('/api/proxy-image', window.location.href);
      proxyUrl.searchParams.set('url', url);

      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Scale to configured width for file size optimization
        // 600px = ~4.5MB per frame, 800px = ~8MB per frame, 1200px = ~18MB per frame
        const ratio = this.imageWidth / img.width;
        canvas.width = this.imageWidth;
        canvas.height = img.height * ratio;
        
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas);
      };
      img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
      img.src = proxyUrl.href;
    });
  }

  /**
   * Generate filename with timestamp in UTC
   * Format: goes-ir-YYYY-MM-DD-HH.gif (e.g., goes-ir-2026-04-28-19.gif)
   */
  generateFilename() {
    const now = new Date();
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, '0');
    const day = String(now.getUTCDate()).padStart(2, '0');
    const hour = String(now.getUTCHours()).padStart(2, '0');
    return `goes-ir-${year}-${month}-${day}-${hour}.gif`;
  }

  /**
   * Create GIF from canvas images using gif.js library
   * @param {Array} canvases - Array of canvas elements
   */
  async createGif(canvases) {
    if (typeof GIF === 'undefined') {
      throw new Error('GIF.js library not loaded. Please ensure gif.js is loaded from CDN.');
    }

    return new Promise((resolve, reject) => {
      const gif = new GIF({
        workers: 2,
        quality: this.gifQuality,  // Reduced quality = smaller file size
        width: canvases[0].width,
        height: canvases[0].height,
        dither: this.ditherMode,  // Enable dithering for better compression
        workerScript: new URL('/lib/gif.worker.js', window.location.href).href,
      });

      // Add each frame with configurable delay
      canvases.forEach(canvas => {
        gif.addFrame(canvas, { delay: this.frameDelayMs });
      });

      gif.on('finished', function(blob) {
        resolve(blob);
      });

      gif.on('error', function(error) {
        reject(new Error(`GIF creation error: ${error.message}`));
      });

      gif.on('progress', function(progress) {
        const statusEl = document.getElementById('gif-download-status');
        if (statusEl) {
          const percentage = Math.round(progress * 100);
          statusEl.textContent = `Encoding GIF: ${percentage}%`;
        }
      });

      gif.render();
    });
  }

  /**
   * Trigger browser download of blob
   */
  downloadGif(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up after a short delay to ensure download starts
    setTimeout(() => URL.revokeObjectURL(url), 100);
  }

  /**
   * Main download function - orchestrates the entire GIF creation process
   */
  async downloadAsGif() {
    if (this.isProcessing) {
      console.warn('GIF creation already in progress');
      return;
    }

    this.isProcessing = true;
    const statusEl = document.getElementById('gif-download-status');
    const downloadBtn = document.getElementById('gif-download-btn');
    
    try {
      // Disable button and show status
      if (downloadBtn) downloadBtn.disabled = true;
      if (statusEl) statusEl.textContent = `Extracting (${this.frameSkip}x skip, ${this.imageWidth}px, q${this.gifQuality})...`;

      const imageData = this.extractImageUrls();
      
      console.log(`Extracted ${imageData.length} images from looper`);
      
      if (imageData.length === 0) {
        throw new Error('No images found in looper. Please ensure the looper has loaded and is displaying images.');
      }

      console.log(`Found ${imageData.length} images, fetching...`);
      if (statusEl) statusEl.textContent = `Fetching ${imageData.length} images...`;

      // Fetch all images and convert to canvas
      // This can take a while for many images
      const canvases = await Promise.all(
        imageData.map(img => this.fetchAndCanvasImage(img.url))
      );

      console.log(`All images fetched, creating GIF from ${canvases.length} frames...`);
      if (statusEl) statusEl.textContent = 'Creating GIF animation...';

      // Create GIF (this shows progress via 'progress' event)
      const gifBlob = await this.createGif(canvases);

      // Generate filename and trigger download
      const filename = this.generateFilename();
      const fileSizeMB = (gifBlob.size / 1024 / 1024).toFixed(1);
      const animationSeconds = (canvases.length * this.frameDelayMs / 1000).toFixed(1);
      
      console.log(`GIF created (${fileSizeMB}MB, ${animationSeconds}s animation), downloading as ${filename}`);
      if (statusEl) statusEl.textContent = `Downloading ${filename}...`;

      this.downloadGif(gifBlob, filename);

      // Success message
      if (statusEl) {
        statusEl.textContent = `✓ ${filename} (${fileSizeMB}MB, ${animationSeconds}s) downloaded`;
        statusEl.style.color = '#5cb85c';
        setTimeout(() => {
          statusEl.textContent = '';
          statusEl.style.color = '';
        }, 4000);
      }
      
    } catch (error) {
      console.error('GIF creation failed:', error);
      if (statusEl) {
        statusEl.textContent = `✗ Error: ${error.message}`;
        statusEl.style.color = '#d9534f';
        setTimeout(() => {
          statusEl.textContent = '';
          statusEl.style.color = '';
        }, 5000);
      }
    } finally {
      this.isProcessing = false;
      if (downloadBtn) downloadBtn.disabled = false;
    }
  }
}

// Initialize immediately when script loads (or when DOM ready, whichever comes first)
function initializeGifDownloader() {
  if (!window.goesGifDownloader) {
    window.goesGifDownloader = new GOESIRGifDownloader();
    // Auto-attach event listener to button if it exists
    const downloadBtn = document.getElementById('gif-download-btn');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', () => {
        window.goesGifDownloader.downloadAsGif();
      });
    }
  }
}

// Try to initialize immediately (script loaded in body)
if (document.readyState === 'loading') {
  // DOM still loading, wait for DOMContentLoaded
  document.addEventListener('DOMContentLoaded', initializeGifDownloader);
} else {
  // DOM already loaded, initialize immediately
  initializeGifDownloader();
}

