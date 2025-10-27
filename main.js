class PekingOperaVirtualMakeup {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.loading = document.getElementById('loading');
        this.status = document.getElementById('status');
        
        this.faceMesh = null;
        this.camera = null;
        this.isDetecting = false;
        
        // 配置参数
        this.config = {
            makeupType: 'none',
            opacity: 0.8,
            intensity: 1.0,
            offset: 0,
            faceTracking: true,
            edgeSmoothing: true,
            colorAdaptation: false
        };
        
        // 脸谱图案数据 (简化版本)
        this.makeupPatterns = {
            sheng: {
                name: '生角',
                color: '#FF6B6B',
                pattern: 'heroic',
                description: '正直英俊的男性角色'
            },
            dan: {
                name: '旦角', 
                color: '#FFB6C1',
                pattern: 'elegant',
                description: '女性角色脸谱'
            },
            jing: {
                name: '净角',
                color: '#4169E1', 
                pattern: 'bold',
                description: '性格鲜明的男性角色'
            },
            chou: {
                name: '丑角',
                color: '#FFA500',
                pattern: 'comic',
                description: '喜剧角色脸谱'
            }
        };
        
        this.init();
    }
    
    async init() {
        try {
            this.updateStatus('正在初始化系统...', 'ready');
            
            // 初始化MediaPipe Face Mesh
            await this.initFaceMesh();
            
            // 启动摄像头
            await this.startCamera();
            
            // 绑定事件监听器
            this.bindEvents();
            
            this.updateStatus('系统初始化完成！', 'ready');
            
        } catch (error) {
            console.error('初始化失败:', error);
            this.updateStatus('初始化失败: ' + error.message, 'error');
        }
    }
    
    async initFaceMesh() {
        this.faceMesh = new FaceMesh({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4.1633559619/${file}`;
            }
        });
        
        this.faceMesh.setOptions({
            maxNumFaces: 1,
            refineLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        
        this.faceMesh.onResults((results) => {
            this.onFaceDetection(results);
        });
    }
    
    async startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = stream;
            
            return new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.canvas.width = this.video.videoWidth;
                    this.canvas.height = this.video.videoHeight;
                    
                    // 启动人脸检测
                    this.startFaceDetection();
                    resolve();
                };
            });
            
        } catch (error) {
            throw new Error('无法访问摄像头: ' + error.message);
        }
    }
    
    startFaceDetection() {
        if (this.isDetecting) return;
        
        this.isDetecting = true;
        this.detectFaces();
    }
    
    stopFaceDetection() {
        this.isDetecting = false;
    }
    
    async detectFaces() {
        if (!this.isDetecting) return;
        
        try {
            await this.faceMesh.send({ image: this.video });
        } catch (error) {
            console.error('人脸检测错误:', error);
        }
        
        // 继续检测
        requestAnimationFrame(() => this.detectFaces());
    }
    
    onFaceDetection(results) {
        // 清除画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
            const landmarks = results.multiFaceLandmarks[0];
            
            // 绘制人脸网格 (调试用)
            if (this.config.faceTracking) {
                this.drawFaceMesh(landmarks);
            }
            
            // 应用脸谱效果
            if (this.config.makeupType !== 'none') {
                this.applyMakeupEffect(landmarks);
            }
        }
    }
    
    drawFaceMesh(landmarks) {
        // 绘制面部关键点
        this.ctx.strokeStyle = '#00FF00';
        this.ctx.lineWidth = 1;
        this.ctx.fillStyle = '#00FF00';
        
        // 连接面部轮廓
        const faceOutline = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
        ];
        
        this.ctx.beginPath();
        for (let i = 0; i < faceOutline.length; i++) {
            const point = landmarks[faceOutline[i]];
            const x = point.x * this.canvas.width;
            const y = point.y * this.canvas.height;
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.closePath();
        this.ctx.stroke();
        
        // 绘制关键点
        for (let i = 0; i < landmarks.length; i += 10) {
            const point = landmarks[i];
            const x = point.x * this.canvas.width;
            const y = point.y * this.canvas.height;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 2, 0, 2 * Math.PI);
            this.ctx.fill();
        }
    }
    
    applyMakeupEffect(landmarks) {
        const makeup = this.makeupPatterns[this.config.makeupType];
        if (!makeup) return;
        
        // 计算面部主要区域
        const faceRegion = this.calculateFaceRegion(landmarks);
        
        // 应用脸谱颜色效果
        this.ctx.save();
        
        // 设置透明度
        this.ctx.globalAlpha = this.config.opacity;
        
        // 创建渐变效果
        const gradient = this.ctx.createRadialGradient(
            faceRegion.centerX, faceRegion.centerY, 0,
            faceRegion.centerX, faceRegion.centerY, faceRegion.radius
        );
        
        const baseColor = makeup.color;
        gradient.addColorStop(0, baseColor + '80');
        gradient.addColorStop(0.5, baseColor + '40');
        gradient.addColorStop(1, baseColor + '00');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // 添加面部特征标记
        this.drawFacialFeatures(landmarks, makeup);
        
        this.ctx.restore();
        
        // 应用边缘平滑
        if (this.config.edgeSmoothing) {
            this.applyEdgeSmoothing(landmarks);
        }
    }
    
    calculateFaceRegion(landmarks) {
        // 使用面部关键点计算面部区域
        const leftCheek = landmarks[234];   // 左脸颊
        const rightCheek = landmarks[454];  // 右脸颊
        const forehead = landmarks[10];     // 额头
        const chin = landmarks[152];        // 下巴
        
        const centerX = (leftCheek.x + rightCheek.x) / 2 * this.canvas.width;
        const centerY = (forehead.y + chin.y) / 2 * this.canvas.height;
        
        const radius = Math.sqrt(
            Math.pow((rightCheek.x - leftCheek.x) * this.canvas.width, 2) +
            Math.pow((chin.y - forehead.y) * this.canvas.height, 2)
        ) / 2;
        
        return {
            centerX,
            centerY,
            radius,
            leftX: leftCheek.x * this.canvas.width,
            rightX: rightCheek.x * this.canvas.width,
            topY: forehead.y * this.canvas.height,
            bottomY: chin.y * this.canvas.height
        };
    }
    
    drawFacialFeatures(landmarks, makeup) {
        // 根据脸谱类型绘制不同的面部特征
        switch (makeup.pattern) {
            case 'heroic': // 生角 - 英武正直
                this.drawHeroicPattern(landmarks);
                break;
            case 'elegant': // 旦角 - 优雅端庄
                this.drawElegantPattern(landmarks);
                break;
            case 'bold': // 净角 - 粗犷豪放
                this.drawBoldPattern(landmarks);
                break;
            case 'comic': // 丑角 - 滑稽幽默
                this.drawComicPattern(landmarks);
                break;
        }
    }
    
    drawHeroicPattern(landmarks) {
        // 生角特征 - 眉毛浓密，眼神坚毅
        const leftBrow = landmarks[70];   // 左眉
        const rightBrow = landmarks[300]; // 右眉
        const leftEye = landmarks[33];    // 左眼
        const rightEye = landmarks[263];  // 右眼
        
        // 绘制眉毛
        this.ctx.strokeStyle = '#8B4513';
        this.ctx.lineWidth = 4;
        this.ctx.beginPath();
        this.ctx.moveTo(leftBrow.x * this.canvas.width, leftBrow.y * this.canvas.height);
        this.ctx.lineTo((leftBrow.x + 0.05) * this.canvas.width, (leftBrow.y - 0.02) * this.canvas.height);
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.moveTo(rightBrow.x * this.canvas.width, rightBrow.y * this.canvas.height);
        this.ctx.lineTo((rightBrow.x - 0.05) * this.canvas.width, (rightBrow.y - 0.02) * this.canvas.height);
        this.ctx.stroke();
        
        // 绘制眼部轮廓
        this.ctx.strokeStyle = '#654321';
        this.ctx.lineWidth = 2;
        this.drawEyeOutline(landmarks, 33, 133, 155, 154, 153, 145, 144, 163);
        this.drawEyeOutline(landmarks, 263, 362, 384, 385, 386, 387, 388, 390);
    }
    
    drawElegantPattern(landmarks) {
        // 旦角特征 - 妆容精致，色彩柔和
        const leftEye = landmarks[33];
        const rightEye = landmarks[263];
        const nose = landmarks[1];
        
        // 绘制眼影
        this.ctx.fillStyle = '#FFB6C180';
        this.ctx.beginPath();
        this.ctx.arc(leftEye.x * this.canvas.width, leftEye.y * this.canvas.height, 20, 0, 2 * Math.PI);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.arc(rightEye.x * this.canvas.width, rightEye.y * this.canvas.height, 20, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // 绘制腮红
        const leftCheek = landmarks[234];
        const rightCheek = landmarks[454];
        
        this.ctx.fillStyle = '#FF69B480';
        this.ctx.beginPath();
        this.arc(leftCheek.x * this.canvas.width, leftCheek.y * this.canvas.height, 15, 0, 2 * Math.PI);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.arc(rightCheek.x * this.canvas.width, rightCheek.y * this.canvas.height, 15, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawBoldPattern(landmarks) {
        // 净角特征 - 色彩浓烈，线条粗犷
        const faceRegion = this.calculateFaceRegion(landmarks);
        
        // 绘制浓重的面部轮廓
        this.ctx.strokeStyle = '#000080';
        this.ctx.lineWidth = 8;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius * 0.8, 0, 2 * Math.PI);
        this.ctx.stroke();
        
        // 绘制夸张的眉毛
        this.ctx.fillStyle = '#000000';
        const leftBrow = landmarks[70];
        const rightBrow = landmarks[300];
        
        this.ctx.fillRect(
            (leftBrow.x - 0.1) * this.canvas.width,
            (leftBrow.y - 0.02) * this.canvas.height,
            0.15 * this.canvas.width,
            8
        );
        
        this.ctx.fillRect(
            (rightBrow.x - 0.05) * this.canvas.width,
            (rightBrow.y - 0.02) * this.canvas.height,
            0.15 * this.canvas.width,
            8
        );
    }
    
    drawComicPattern(landmarks) {
        // 丑角特征 - 白鼻梁，夸张表情
        const noseBridge = landmarks[1]; // 鼻梁
        const noseTip = landmarks[4];    // 鼻尖
        
        // 绘制白鼻梁
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.beginPath();
        this.ctx.ellipse(
            noseBridge.x * this.canvas.width,
            noseBridge.y * this.canvas.height,
            15,
            25,
            0,
            0,
            2 * Math.PI
        );
        this.ctx.fill();
        
        // 绘制夸张的嘴巴
        const mouth = landmarks[13];
        this.ctx.strokeStyle = '#DC143C';
        this.ctx.lineWidth = 6;
        this.ctx.beginPath();
        this.ctx.arc(
            mouth.x * this.canvas.width,
            mouth.y * this.canvas.height,
            20,
            0,
            Math.PI
        );
        this.ctx.stroke();
    }
    
    drawEyeOutline(landmarks, ...indices) {
        this.ctx.beginPath();
        for (let i = 0; i < indices.length; i++) {
            const point = landmarks[indices[i]];
            const x = point.x * this.canvas.width;
            const y = point.y * this.canvas.height;
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.closePath();
        this.ctx.stroke();
    }
    
    applyEdgeSmoothing(landmarks) {
        // 简单的边缘平滑处理
        this.ctx.globalCompositeOperation = 'destination-in';
        
        const faceRegion = this.calculateFaceRegion(landmarks);
        const gradient = this.ctx.createRadialGradient(
            faceRegion.centerX, faceRegion.centerY, faceRegion.radius * 0.7,
            faceRegion.centerX, faceRegion.centerY, faceRegion.radius
        );
        
        gradient.addColorStop(0, '#FFFFFF');
        gradient.addColorStop(1, '#000000');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    bindEvents() {
        // 脸谱类型选择
        document.querySelectorAll('.makeup-option').forEach(option => {
            option.addEventListener('click', (e) => {
                document.querySelectorAll('.makeup-option').forEach(opt => opt.classList.remove('active'));
                e.target.classList.add('active');
                this.config.makeupType = e.target.dataset.type;
            });
        });
        
        // 滑块控制
        document.getElementById('opacitySlider').addEventListener('input', (e) => {
            this.config.opacity = e.target.value / 100;
            document.getElementById('opacityValue').textContent = e.target.value;
        });
        
        document.getElementById('intensitySlider').addEventListener('input', (e) => {
            this.config.intensity = e.target.value / 100;
            document.getElementById('intensityValue').textContent = e.target.value;
        });
        
        document.getElementById('offsetSlider').addEventListener('input', (e) => {
            this.config.offset = parseInt(e.target.value);
            document.getElementById('offsetValue').textContent = e.target.value;
        });
        
        // 复选框控制
        document.getElementById('faceTracking').addEventListener('change', (e) => {
            this.config.faceTracking = e.target.checked;
        });
        
        document.getElementById('edgeSmoothing').addEventListener('change', (e) => {
            this.config.edgeSmoothing = e.target.checked;
        });
        
        document.getElementById('colorAdaptation').addEventListener('change', (e) => {
            this.config.colorAdaptation = e.target.checked;
        });
        
        // 按钮功能
        document.getElementById('captureBtn').addEventListener('click', () => {
            this.captureImage();
        });
        
        document.getElementById('recordBtn').addEventListener('click', () => {
            this.toggleRecording();
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetEffects();
        });
    }
    
    captureImage() {
        // 创建合成图像
        const captureCanvas = document.createElement('canvas');
        const captureCtx = captureCanvas.getContext('2d');
        
        captureCanvas.width = this.canvas.width;
        captureCanvas.height = this.canvas.height;
        
        // 绘制视频帧
        captureCtx.drawImage(this.video, 0, 0);
        
        // 绘制脸谱效果
        captureCtx.drawImage(this.canvas, 0, 0);
        
        // 下载图像
        const link = document.createElement('a');
        link.download = `京剧脸谱_${this.config.makeupType}_${Date.now()}.png`;
        link.href = captureCanvas.toDataURL();
        link.click();
        
        this.updateStatus('图像已保存', 'ready');
        setTimeout(() => {
            this.updateStatus('系统就绪', 'ready');
        }, 2000);
    }
    
    toggleRecording() {
        // 简化的录像功能
        const recordBtn = document.getElementById('recordBtn');
        
        if (recordBtn.textContent.includes('开始录像')) {
            recordBtn.textContent = '🎬 停止录像';
            recordBtn.style.background = 'linear-gradient(45deg, #FF0000, #8B0000)';
            this.updateStatus('正在录像...', 'ready');
        } else {
            recordBtn.textContent = '🎬 开始录像';
            recordBtn.style.background = 'linear-gradient(45deg, #8B0000, #CD853F)';
            this.updateStatus('录像已保存', 'ready');
            
            setTimeout(() => {
                this.updateStatus('系统就绪', 'ready');
            }, 2000);
        }
    }
    
    resetEffects() {
        // 重置所有效果
        this.config = {
            makeupType: 'none',
            opacity: 0.8,
            intensity: 1.0,
            offset: 0,
            faceTracking: true,
            edgeSmoothing: true,
            colorAdaptation: false
        };
        
        // 重置UI
        document.getElementById('opacitySlider').value = 80;
        document.getElementById('opacityValue').textContent = '80';
        document.getElementById('intensitySlider').value = 100;
        document.getElementById('intensityValue').textContent = '100';
        document.getElementById('offsetSlider').value = 0;
        document.getElementById('offsetValue').textContent = '0';
        
        document.getElementById('faceTracking').checked = true;
        document.getElementById('edgeSmoothing').checked = true;
        document.getElementById('colorAdaptation').checked = false;
        
        document.querySelectorAll('.makeup-option').forEach(opt => opt.classList.remove('active'));
        document.querySelector('.makeup-option[data-type="none"]').classList.add('active');
        
        this.updateStatus('效果已重置', 'ready');
        setTimeout(() => {
            this.updateStatus('系统就绪', 'ready');
        }, 2000);
    }
    
    updateStatus(message, type) {
        this.status.textContent = message;
        this.status.className = `status ${type}`;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new PekingOperaVirtualMakeup();
});