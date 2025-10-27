// 京剧脸谱图案数据库
const PEKING_OPERA_MAKEUP_PATTERNS = {
    // 生角脸谱 - 正直英俊的男性角色
    sheng: {
        name: "生角脸谱",
        category: "sheng",
        description: "生角是京剧中的正面男性角色，脸谱相对简洁，突出英俊正直的特征。",
        colors: {
            primary: "#F5DEB3",      // 主色调 - 浅肤色
            secondary: "#8B4513",    // 辅助色 - 深棕色
            accent: "#DC143C"        // 点缀色 - 深红色
        },
        features: {
            eyebrows: "thick",       // 浓眉
            eyes: "bright",          // 明亮的眼睛
            mouth: "natural",        // 自然的嘴巴
            forehead: "clear"        // 清爽的额头
        },
        pattern: {
            // 面部轮廓
            faceOutline: {
                type: "natural",
                color: "#F5DEB3",
                opacity: 0.3
            },
            // 眉毛样式
            eyebrows: {
                style: "straight",     // 直眉
                color: "#8B4513",
                thickness: 6,
                length: 0.15,
                angle: 0
            },
            // 眼部装饰
            eyeDecoration: {
                type: "liner",         // 眼线
                color: "#654321",
                thickness: 2,
                extend: 0.02
            },
            // 脸颊红润
            blush: {
                color: "#FFB6C1",
                opacity: 0.4,
                size: 15,
                position: "cheekbone"
            }
        },
        // 关键点映射
        landmarkMapping: {
            leftEyebrow: [70, 107, 66, 105, 63, 70],
            rightEyebrow: [300, 336, 296, 334, 293, 300],
            leftEye: [33, 133, 155, 154, 153, 145, 144, 163],
            rightEye: [263, 362, 384, 385, 386, 387, 388, 390],
            nose: [1, 2, 3, 4, 5, 6, 168, 197, 195, 5],
            mouth: [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82]
        }
    },
    
    // 旦角脸谱 - 女性角色
    dan: {
        name: "旦角脸谱",
        category: "dan", 
        description: "旦角是女性角色的统称，脸谱注重表现女性的柔美和端庄。",
        colors: {
            primary: "#FFE4E1",      // 主色调 - 淡粉色
            secondary: "#FFB6C1",    // 辅助色 - 浅粉色
            accent: "#FF69B4"        // 点缀色 - 粉红色
        },
        features: {
            eyebrows: "slender",     // 细眉
            eyes: "charming",        // 迷人的眼睛
            mouth: "delicate",       // 精致的嘴巴
            forehead: "elegant"      // 优雅的额头
        },
        pattern: {
            faceOutline: {
                type: "soft",
                color: "#FFE4E1",
                opacity: 0.4
            },
            eyebrows: {
                style: "curved",       // 弯眉
                color: "#8B4513",
                thickness: 3,
                length: 0.12,
                angle: 15
            },
            eyeDecoration: {
                type: "shadow",        // 眼影
                color: "#FFB6C1",
                thickness: 8,
                gradient: true
            },
            blush: {
                color: "#FF69B4",
                opacity: 0.6,
                size: 18,
                position: "apple"
            },
            lipColor: {
                color: "#DC143C",
                opacity: 0.7
            }
        },
        landmarkMapping: {
            leftEyebrow: [70, 107, 66, 105, 63, 70],
            rightEyebrow: [300, 336, 296, 334, 293, 300],
            leftEye: [33, 133, 155, 154, 153, 145, 144, 163],
            rightEye: [263, 362, 384, 385, 386, 387, 388, 390],
            nose: [1, 2, 3, 4, 5, 6, 168, 197, 195, 5],
            mouth: [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82]
        }
    },
    
    // 净角脸谱 - 性格鲜明的男性角色
    jing: {
        name: "净角脸谱",
        category: "jing",
        description: "净角多为性格鲜明的男性角色，脸谱色彩浓烈，图案复杂，富有表现力。",
        colors: {
            primary: "#4169E1",      // 主色调 - 皇家蓝
            secondary: "#000080",    // 辅助色 - 深蓝色
            accent: "#FFD700"        // 点缀色 - 金色
        },
        features: {
            eyebrows: "bold",        // 粗眉
            eyes: "fierce",          // 凶猛的眼睛
            mouth: "strong",         // 有力的嘴巴
            forehead: "patterned"    // 有图案的额头
        },
        pattern: {
            faceOutline: {
                type: "bold",
                color: "#4169E1",
                opacity: 0.7
            },
            eyebrows: {
                style: "upturned",     // 上挑眉
                color: "#000000",
                thickness: 10,
                length: 0.2,
                angle: 30
            },
            eyeDecoration: {
                type: "dramatic",      // 戏剧化眼妆
                color: "#FFD700",
                thickness: 5,
                extended: true
            },
            facePatterns: {
                forehead: "tiger",     // 额头虎纹
                cheeks: "whisker",     // 脸颊胡须
                chin: "beard"          // 下巴胡须
            },
            lines: {
                color: "#000000",
                thickness: 4,
                style: "bold"
            }
        },
        landmarkMapping: {
            leftEyebrow: [70, 107, 66, 105, 63, 70],
            rightEyebrow: [300, 336, 296, 334, 293, 300],
            leftEye: [33, 133, 155, 154, 153, 145, 144, 163],
            rightEye: [263, 362, 384, 385, 386, 387, 388, 390],
            nose: [1, 2, 3, 4, 5, 6, 168, 197, 195, 5],
            mouth: [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82],
            forehead: [10, 109, 67, 103, 54, 21, 162, 127],
            chin: [152, 377, 400, 378, 379, 365, 397, 288]
        }
    },
    
    // 丑角脸谱 - 喜剧角色
    chou: {
        name: "丑角脸谱",
        category: "chou",
        description: "丑角是喜剧角色，脸谱特征鲜明，通常在鼻梁处涂抹白色，形成滑稽的效果。",
        colors: {
            primary: "#FFFFFF",      // 主色调 - 白色
            secondary: "#FFA500",    // 辅助色 - 橙色
            accent: "#FF0000"        // 点缀色 - 红色
        },
        features: {
            eyebrows: "funny",       // 滑稽的眉毛
            eyes: "comical",         // 喜剧化的眼睛
            mouth: "smiling",        // 微笑的嘴巴
            nose: "white"            // 白色的鼻子
        },
        pattern: {
            faceOutline: {
                type: "round",
                color: "#FFA500",
                opacity: 0.5
            },
            eyebrows: {
                style: "curved",       // 弯曲的眉毛
                color: "#000000",
                thickness: 5,
                length: 0.1,
                angle: 45
            },
            nose: {
                type: "white_patch",   // 白色鼻贴
                color: "#FFFFFF",
                size: 30,
                shape: "oval"
            },
            mouth: {
                style: "exaggerated",  // 夸张的嘴巴
                color: "#DC143C",
                thickness: 8,
                curve: 0.5
            },
            facePatterns: {
                freckles: true,        // 雀斑
                wrinkles: true,        // 皱纹
                spots: true            // 斑点
            }
        },
        landmarkMapping: {
            leftEyebrow: [70, 107, 66, 105, 63, 70],
            rightEyebrow: [300, 336, 296, 334, 293, 300],
            leftEye: [33, 133, 155, 154, 153, 145, 144, 163],
            rightEye: [263, 362, 384, 385, 386, 387, 388, 390],
            nose: [1, 2, 3, 4, 5, 6, 168, 197, 195, 5],
            mouth: [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82]
        }
    }
};

// 经典角色脸谱示例
const CLASSIC_CHARACTERS = {
    guanyu: {
        name: "关羽",
        baseType: "jing",
        description: "三国名将，以忠义著称，脸谱为红色，象征忠勇。",
        customizations: {
            colors: {
                primary: "#DC143C",      // 深红色
                secondary: "#8B0000",    // 暗红色
                accent: "#000000"        // 黑色
            },
            pattern: {
                faceOutline: {
                    color: "#DC143C",
                    opacity: 0.8
                },
                eyebrows: {
                    style: "phoenix",      // 凤眉
                    color: "#000000",
                    thickness: 12
                },
                eyeDecoration: {
                    type: "phoenix_eye",   // 凤眼
                    color: "#FFD700"
                },
                forehead: {
                    pattern: "phoenix",    // 额头凤凰图案
                    color: "#FFD700",
                    size: 40
                }
            }
        }
    },
    
    baozheng: {
        name: "包拯",
        baseType: "jing",
        description: "北宋名臣，以廉洁公正闻名，脸谱为黑色，象征刚直不阿。",
        customizations: {
            colors: {
                primary: "#000000",      // 纯黑色
                secondary: "#2F4F4F",    // 深灰色
                accent: "#FFFFFF"        // 白色
            },
            pattern: {
                faceOutline: {
                    color: "#000000",
                    opacity: 0.9
                },
                eyebrows: {
                    style: "sword",        // 剑眉
                    color: "#FFFFFF",
                    thickness: 8
                },
                eyeDecoration: {
                    type: "stern_eye",     // 威严的眼神
                    color: "#FFFFFF"
                },
                forehead: {
                    pattern: "moon",       // 月牙图案
                    color: "#FFFFFF",
                    size: 25,
                    position: "center"
                },
                cheeks: {
                    pattern: "whisker",    // 胡须
                    color: "#000000",
                    style: "full_beard"
                }
            }
        }
    },
    
    caocao: {
        name: "曹操",
        baseType: "jing",
        description: "三国时期著名政治家，脸谱为白色，象征奸诈多疑。",
        customizations: {
            colors: {
                primary: "#FFFFFF",      // 白色
                secondary: "#F5F5DC",    // 米色
                accent: "#8B4513"        // 棕色
            },
            pattern: {
                faceOutline: {
                    color: "#FFFFFF",
                    opacity: 0.7
                },
                eyebrows: {
                    style: "slanted",      // 斜眉
                    color: "#000000",
                    thickness: 6,
                    angle: 20
                },
                eyeDecoration: {
                    type: "sly_eye",       // 狡猾的眼神
                    color: "#8B4513",
                    thickness: 3
                },
                lines: {
                    forehead: "worry",     // 额头皱纹
                    eyes: "crow_feet",     // 鱼尾纹
                    mouth: "smirk"         // 奸笑
                }
            }
        }
    }
};

// 导出数据
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PEKING_OPERA_MAKEUP_PATTERNS,
        CLASSIC_CHARACTERS
    };
}