// 高级京剧脸谱渲染引擎
class AdvancedMakeupRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        
        // 渲染配置
        this.config = {
            quality: 'high',           // 渲染质量
            antiAliasing: true,        // 抗锯齿
            shadowQuality: 'medium',   // 阴影质量
            blendMode: 'normal'        // 混合模式
        };
        
        // 缓存对象
        this.cache = {
            gradients: new Map(),
            patterns: new Map(),
            transforms: new Map()
        };
    }
    
    // 主渲染函数
    render(landmarks, makeupType, options = {}) {
        if (!landmarks || !makeupType) return;
        
        // 保存画布状态
        this.ctx.save();
        
        try {
            // 应用全局设置
            this.applyGlobalSettings(options);
            
            // 计算面部区域
            const faceRegion = this.calculateFaceRegion(landmarks);
            
            // 渲染基础面部轮廓
            this.renderFaceOutline(landmarks, makeupType, faceRegion, options);
            
            // 渲染眉毛
            this.renderEyebrows(landmarks, makeupType, options);
            
            // 渲染眼部装饰
            this.renderEyeDecoration(landmarks, makeupType, options);
            
            // 渲染鼻部装饰
            this.renderNoseDecoration(landmarks, makeupType, options);
            
            // 渲染脸颊装饰
            this.renderCheekDecoration(landmarks, makeupType, options);
            
            // 渲染嘴部装饰
            this.renderMouthDecoration(landmarks, makeupType, options);
            
            // 渲染额头装饰
            this.renderForeheadDecoration(landmarks, makeupType, options);
            
            // 应用后期效果
            this.applyPostEffects(landmarks, options);
            
        } catch (error) {
            console.error('渲染错误:', error);
        } finally {
            // 恢复画布状态
            this.ctx.restore();
        }
    }
    
    // 应用全局设置
    applyGlobalSettings(options) {
        // 设置抗锯齿
        if (this.config.antiAliasing) {
            this.ctx.imageSmoothingEnabled = true;
            this.ctx.imageSmoothingQuality = 'high';
        }
        
        // 设置混合模式
        if (options.blendMode) {
            this.ctx.globalCompositeOperation = options.blendMode;
        }
        
        // 设置全局透明度
        if (options.opacity !== undefined) {
            this.ctx.globalAlpha = options.opacity;
        }
    }
    
    // 计算面部区域
    calculateFaceRegion(landmarks) {
        // 获取关键面部点
        const leftCheek = landmarks[234];
        const rightCheek = landmarks[454];
        const forehead = landmarks[10];
        const chin = landmarks[152];
        const nose = landmarks[1];
        
        // 计算边界框
        const minX = Math.min(leftCheek.x, rightCheek.x, forehead.x, chin.x);
        const maxX = Math.max(leftCheek.x, rightCheek.x, forehead.x, chin.x);
        const minY = Math.min(leftCheek.y, rightCheek.y, forehead.y, chin.y);
        const maxY = Math.max(leftCheek.y, rightCheek.y, forehead.y, chin.y);
        
        // 计算中心点和尺寸
        const centerX = (minX + maxX) / 2 * this.width;
        const centerY = (minY + maxY) / 2 * this.height;
        const width = (maxX - minX) * this.width;
        const height = (maxY - minY) * this.height;
        const radius = Math.max(width, height) / 2;
        
        return {
            centerX,
            centerY,
            width,
            height,
            radius,
            minX: minX * this.width,
            maxX: maxX * this.width,
            minY: minY * this.height,
            maxY: maxY * this.height,
            noseX: nose.x * this.width,
            noseY: nose.y * this.height
        };
    }
    
    // 渲染面部轮廓
    renderFaceOutline(landmarks, makeupType, faceRegion, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.faceOutline) return;
        
        const outline = pattern.pattern.faceOutline;
        
        this.ctx.save();
        
        // 创建渐变
        const gradient = this.ctx.createRadialGradient(
            faceRegion.centerX, faceRegion.centerY, 0,
            faceRegion.centerX, faceRegion.centerY, faceRegion.radius
        );
        
        const baseColor = outline.color || pattern.colors.primary;
        gradient.addColorStop(0, baseColor + Math.floor((outline.opacity || 0.5) * 255).toString(16).padStart(2, '0'));
        gradient.addColorStop(0.7, baseColor + Math.floor((outline.opacity || 0.5) * 0.7 * 255).toString(16).padStart(2, '0'));
        gradient.addColorStop(1, baseColor + '00');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        
        this.ctx.restore();
    }
    
    // 渲染眉毛
    renderEyebrows(landmarks, makeupType, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.eyebrows) return;
        
        const eyebrows = pattern.pattern.eyebrows;
        const leftBrowPoints = pattern.landmarkMapping.leftEyebrow;
        const rightBrowPoints = pattern.landmarkMapping.rightEyebrow;
        
        this.ctx.save();
        this.ctx.strokeStyle = eyebrows.color;
        this.ctx.lineWidth = eyebrows.thickness;
        this.ctx.lineCap = 'round';
        
        // 渲染左眉
        this.renderEyebrowShape(landmarks, leftBrowPoints, eyebrows, 'left');
        
        // 渲染右眉
        this.renderEyebrowShape(landmarks, rightBrowPoints, eyebrows, 'right');
        
        this.ctx.restore();
    }
    
    // 渲染眉毛形状
    renderEyebrowShape(landmarks, browPoints, eyebrowConfig, side) {
        const points = browPoints.map(index => landmarks[index]);
        
        this.ctx.beginPath();
        
        for (let i = 0; i < points.length - 1; i++) {
            const current = points[i];
            const next = points[i + 1];
            
            const x1 = current.x * this.width;
            const y1 = current.y * this.height;
            const x2 = next.x * this.width;
            const y2 = next.y * this.height;
            
            if (i === 0) {
                this.ctx.moveTo(x1, y1);
            }
            
            // 根据眉毛样式调整曲线
            let controlX, controlY;
            
            switch (eyebrowConfig.style) {
                case 'straight':
                    this.ctx.lineTo(x2, y2);
                    break;
                    
                case 'curved':
                    controlX = (x1 + x2) / 2;
                    controlY = Math.min(y1, y2) - eyebrowConfig.thickness * 2;
                    this.ctx.quadraticCurveTo(controlX, controlY, x2, y2);
                    break;
                    
                case 'upturned':
                    controlX = (x1 + x2) / 2;
                    controlY = Math.min(y1, y2) - eyebrowConfig.thickness * 3;
                    this.ctx.quadraticCurveTo(controlX, controlY, x2, y2);
                    break;
                    
                case 'phoenix':
                    // 凤眉 - 更加弯曲和优雅
                    controlX = (x1 + x2) / 2 + (side === 'left' ? -10 : 10);
                    controlY = Math.min(y1, y2) - eyebrowConfig.thickness * 4;
                    this.ctx.quadraticCurveTo(controlX, controlY, x2, y2);
                    break;
            }
        }
        
        this.ctx.stroke();
    }
    
    // 渲染眼部装饰
    renderEyeDecoration(landmarks, makeupType, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.eyeDecoration) return;
        
        const eyeDecoration = pattern.pattern.eyeDecoration;
        const leftEyePoints = pattern.landmarkMapping.leftEye;
        const rightEyePoints = pattern.landmarkMapping.rightEye;
        
        this.ctx.save();
        
        // 渲染左眼装饰
        this.renderEyeMakeup(landmarks, leftEyePoints, eyeDecoration, 'left');
        
        // 渲染右眼装饰
        this.renderEyeMakeup(landmarks, rightEyePoints, eyeDecoration, 'right');
        
        this.ctx.restore();
    }
    
    // 渲染眼部妆容
    renderEyeMakeup(landmarks, eyePoints, decoration, side) {
        const points = eyePoints.map(index => landmarks[index]);
        
        // 计算眼部中心
        const centerX = points.reduce((sum, p) => sum + p.x, 0) / points.length * this.width;
        const centerY = points.reduce((sum, p) => sum + p.y, 0) / points.length * this.height;
        
        switch (decoration.type) {
            case 'liner':
                this.renderEyeLiner(points, decoration);
                break;
                
            case 'shadow':
                this.renderEyeShadow(centerX, centerY, decoration);
                break;
                
            case 'dramatic':
                this.renderDramaticEye(centerX, centerY, decoration, side);
                break;
                
            case 'phoenix_eye':
                this.renderPhoenixEye(centerX, centerY, decoration);
                break;
        }
    }
    
    // 渲染眼线
    renderEyeLiner(points, decoration) {
        this.ctx.strokeStyle = decoration.color;
        this.ctx.lineWidth = decoration.thickness;
        
        // 上眼线
        this.ctx.beginPath();
        for (let i = 0; i < points.length / 2; i++) {
            const point = points[i];
            const x = point.x * this.width;
            const y = point.y * this.height;
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.stroke();
        
        // 下眼线
        this.ctx.beginPath();
        for (let i = points.length / 2; i < points.length; i++) {
            const point = points[i];
            const x = point.x * this.width;
            const y = point.y * this.height;
            
            if (i === points.length / 2) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.stroke();
    }
    
    // 渲染眼影
    renderEyeShadow(centerX, centerY, decoration) {
        const gradient = this.ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, decoration.thickness
        );
        
        gradient.addColorStop(0, decoration.color + '80');
        gradient.addColorStop(1, decoration.color + '00');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, decoration.thickness, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    // 渲染戏剧化眼部
    renderDramaticEye(centerX, centerY, decoration, side) {
        this.ctx.strokeStyle = decoration.color;
        this.ctx.lineWidth = decoration.thickness;
        
        // 绘制延伸的眼线
        const extendX = side === 'left' ? -30 : 30;
        
        this.ctx.beginPath();
        this.ctx.moveTo(centerX, centerY);
        this.ctx.lineTo(centerX + extendX, centerY - 10);
        this.ctx.stroke();
        
        // 添加装饰点
        this.ctx.fillStyle = decoration.color;
        this.ctx.beginPath();
        this.ctx.arc(centerX + extendX, centerY - 10, 3, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    // 渲染凤眼
    renderPhoenixEye(centerX, centerY, decoration) {
        this.ctx.strokeStyle = decoration.color;
        this.ctx.lineWidth = decoration.thickness;
        
        // 绘制凤眼形状
        this.ctx.beginPath();
        this.ctx.ellipse(centerX, centerY, 25, 15, 0, 0, 2 * Math.PI);
        this.ctx.stroke();
        
        // 添加凤尾装饰
        this.ctx.beginPath();
        this.ctx.moveTo(centerX + 25, centerY);
        this.ctx.quadraticCurveTo(centerX + 40, centerY - 10, centerX + 35, centerY - 20);
        this.ctx.stroke();
    }
    
    // 渲染鼻部装饰
    renderNoseDecoration(landmarks, makeupType, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.nose) return;
        
        const nose = pattern.pattern.nose;
        const nosePoints = pattern.landmarkMapping.nose;
        
        this.ctx.save();
        
        switch (nose.type) {
            case 'white_patch':
                this.renderWhiteNosePatch(landmarks, nose, nosePoints);
                break;
        }
        
        this.ctx.restore();
    }
    
    // 渲染白色鼻贴 (丑角特征)
    renderWhiteNosePatch(landmarks, noseConfig, nosePoints) {
        const noseTip = landmarks[1]; // 鼻尖
        const noseBridge = landmarks[168]; // 鼻梁
        
        const centerX = noseTip.x * this.width;
        const centerY = noseTip.y * this.height;
        
        this.ctx.fillStyle = noseConfig.color;
        this.ctx.beginPath();
        
        if (noseConfig.shape === 'oval') {
            this.ctx.ellipse(centerX, centerY, noseConfig.size, noseConfig.size * 1.5, 0, 0, 2 * Math.PI);
        } else {
            this.ctx.arc(centerX, centerY, noseConfig.size, 0, 2 * Math.PI);
        }
        
        this.ctx.fill();
    }
    
    // 渲染脸颊装饰
    renderCheekDecoration(landmarks, makeupType, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.blush) return;
        
        const blush = pattern.pattern.blush;
        const leftCheek = landmarks[234];
        const rightCheek = landmarks[454];
        
        this.ctx.save();
        
        // 渲染左脸颊
        this.renderBlush(leftCheek.x * this.width, leftCheek.y * this.height, blush);
        
        // 渲染右脸颊
        this.renderBlush(rightCheek.x * this.width, rightCheek.y * this.height, blush);
        
        this.ctx.restore();
    }
    
    // 渲染腮红
    renderBlush(x, y, blushConfig) {
        const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, blushConfig.size);
        
        gradient.addColorStop(0, blushConfig.color + Math.floor(blushConfig.opacity * 255).toString(16).padStart(2, '0'));
        gradient.addColorStop(1, blushConfig.color + '00');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(x, y, blushConfig.size, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    // 渲染嘴部装饰
    renderMouthDecoration(landmarks, makeupType, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.mouth) return;
        
        const mouth = pattern.pattern.mouth;
        const mouthPoints = pattern.landmarkMapping.mouth;
        
        this.ctx.save();
        
        switch (mouth.style) {
            case 'exaggerated':
                this.renderExaggeratedMouth(landmarks, mouth);
                break;
        }
        
        this.ctx.restore();
    }
    
    // 渲染夸张的嘴部
    renderExaggeratedMouth(landmarks, mouthConfig) {
        const upperLip = landmarks[13];
        const lowerLip = landmarks[14];
        
        const centerX = (upperLip.x + lowerLip.x) / 2 * this.width;
        const centerY = (upperLip.y + lowerLip.y) / 2 * this.height;
        
        this.ctx.strokeStyle = mouthConfig.color;
        this.ctx.lineWidth = mouthConfig.thickness;
        
        // 绘制夸张的弧形嘴巴
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 25, 0, Math.PI);
        this.ctx.stroke();
        
        // 添加嘴角装饰
        this.ctx.fillStyle = mouthConfig.color;
        this.ctx.beginPath();
        this.ctx.arc(centerX - 25, centerY, 3, 0, 2 * Math.PI);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.arc(centerX + 25, centerY, 3, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    // 渲染额头装饰
    renderForeheadDecoration(landmarks, makeupType, options) {
        const pattern = PEKING_OPERA_MAKEUP_PATTERNS[makeupType];
        if (!pattern || !pattern.pattern.forehead) return;
        
        const forehead = pattern.pattern.forehead;
        const foreheadPoints = pattern.landmarkMapping.forehead;
        
        if (!foreheadPoints) return;
        
        this.ctx.save();
        
        switch (forehead.pattern) {
            case 'tiger':
                this.renderTigerStripe(landmarks, forehead);
                break;
                
            case 'phoenix':
                this.renderPhoenixPattern(landmarks, forehead);
                break;
                
            case 'moon':
                this.renderMoonPattern(landmarks, forehead);
                break;
        }
        
        this.ctx.restore();
    }
    
    // 渲染虎纹
    renderTigerStripe(landmarks, foreheadConfig) {
        const forehead = landmarks[10]; // 额头中心
        
        const centerX = forehead.x * this.width;
        const centerY = forehead.y * this.height;
        
        this.ctx.strokeStyle = foreheadConfig.color;
        this.ctx.lineWidth = foreheadConfig.thickness || 3;
        
        // 绘制垂直虎纹
        for (let i = -2; i <= 2; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(centerX + i * 8, centerY - 20);
            this.ctx.lineTo(centerX + i * 8, centerY + 20);
            this.ctx.stroke();
        }
    }
    
    // 渲染凤凰图案
    renderPhoenixPattern(landmarks, foreheadConfig) {
        const forehead = landmarks[10];
        
        const centerX = forehead.x * this.width;
        const centerY = forehead.y * this.height;
        
        this.ctx.fillStyle = foreheadConfig.color;
        
        // 简化的凤凰图案
        this.ctx.beginPath();
        this.ctx.moveTo(centerX, centerY - foreheadConfig.size);
        this.ctx.quadraticCurveTo(centerX - 15, centerY, centerX, centerY + 15);
        this.ctx.quadraticCurveTo(centerX + 15, centerY, centerX, centerY - foreheadConfig.size);
        this.ctx.fill();
    }
    
    // 渲染月牙图案
    renderMoonPattern(landmarks, foreheadConfig) {
        const forehead = landmarks[10];
        
        const centerX = forehead.x * this.width;
        const centerY = forehead.y * this.height;
        
        this.ctx.fillStyle = foreheadConfig.color;
        
        // 月牙形状
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, foreheadConfig.size, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // 月牙的阴影部分
        this.ctx.globalCompositeOperation = 'destination-out';
        this.ctx.beginPath();
        this.ctx.arc(centerX + 5, centerY, foreheadConfig.size * 0.8, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    // 应用后期效果
    applyPostEffects(landmarks, options) {
        if (options.edgeSmoothing) {
            this.applyEdgeSmoothing(landmarks, options);
        }
        
        if (options.colorAdaptation) {
            this.applyColorAdaptation(landmarks, options);
        }
        
        if (options.shadowQuality !== 'none') {
            this.applyShadowEffects(landmarks, options);
        }
    }
    
    // 应用边缘平滑
    applyEdgeSmoothing(landmarks, options) {
        const faceRegion = this.calculateFaceRegion(landmarks);
        
        // 创建边缘遮罩
        const gradient = this.ctx.createRadialGradient(
            faceRegion.centerX, faceRegion.centerY, faceRegion.radius * 0.8,
            faceRegion.centerX, faceRegion.centerY, faceRegion.radius
        );
        
        gradient.addColorStop(0, '#FFFFFF');
        gradient.addColorStop(0.8, '#FFFFFF');
        gradient.addColorStop(1, '#000000');
        
        this.ctx.globalCompositeOperation = 'destination-in';
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    // 应用颜色自适应
    applyColorAdaptation(landmarks, options) {
        // 根据面部光照调整颜色
        // 这里可以实现更复杂的颜色适应算法
        const faceRegion = this.calculateFaceRegion(landmarks);
        
        // 模拟光照适应
        const lightGradient = this.ctx.createRadialGradient(
            faceRegion.centerX - 30, faceRegion.centerY - 30, 0,
            faceRegion.centerX - 30, faceRegion.centerY - 30, 60
        );
        
        lightGradient.addColorStop(0, 'rgba(255, 255, 255, 0.2)');
        lightGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        this.ctx.globalCompositeOperation = 'soft-light';
        this.ctx.fillStyle = lightGradient;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    // 应用阴影效果
    applyShadowEffects(landmarks, options) {
        const faceRegion = this.calculateFaceRegion(landmarks);
        
        // 添加面部阴影
        const shadowGradient = this.ctx.createRadialGradient(
            faceRegion.centerX + 20, faceRegion.centerY + 20, 0,
            faceRegion.centerX + 20, faceRegion.centerY + 20, 40
        );
        
        shadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.3)');
        shadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        
        this.ctx.globalCompositeOperation = 'multiply';
        this.ctx.fillStyle = shadowGradient;
        this.ctx.beginPath();
        this.ctx.arc(faceRegion.centerX, faceRegion.centerY, faceRegion.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    // 清除缓存
    clearCache() {
        this.cache.gradients.clear();
        this.cache.patterns.clear();
        this.cache.transforms.clear();
    }
    
    // 更新配置
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }
    
    // 获取渲染统计
    getStats() {
        return {
            gradientsCached: this.cache.gradients.size,
            patternsCached: this.cache.patterns.size,
            transformsCached: this.cache.transforms.size
        };
    }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedMakeupRenderer;
}