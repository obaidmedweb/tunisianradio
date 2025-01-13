import sys
import vlc
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QPushButton, QLabel, QComboBox,
                           QTabWidget, QFrame, QGridLayout, QScrollArea,
                           QSizePolicy, QSlider)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt, QSize, QTimer

class CustomButton(QPushButton):
    def __init__(self, text, icon_path=None, is_control=False):
        super().__init__(text)
        self.setFont(QFont('Arial', 11))
        self.setMinimumHeight(45 if is_control else 40)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Different styles for control buttons vs channel buttons
        if is_control:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 22px;
                    padding: 10px 30px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #2196F3;
                    border: 2px solid #2196F3;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #1976D2;
                    color: white;
                }
            """)

class CategoryWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 20)
        
        # Category header
        header = QWidget()
        header.setStyleSheet("""
            background-color: #E3F2FD;
            border-radius: 8px;
            padding: 5px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 8, 15, 8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1565C0;")
        header_layout.addWidget(title_label)
        
        layout.addWidget(header)
        
        # Content widget
        self.content = QWidget()
        self.content_layout = QGridLayout(self.content)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(5, 10, 5, 5)
        layout.addWidget(self.content)

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اي بي اي في عربي - Arab Media IPTV")
        self.setMinimumSize(1200, 800)
        
        # Initialize VLC instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_media = None
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Create header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Create logo
        logo_label = QLabel()
        logo_label.setFixedSize(70, 70)
        logo_label.setStyleSheet("""
            background-color: #2196F3;
            border-radius: 35px;
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setText("AM")
        header_layout.addWidget(logo_label)
        
        # Create title container
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(5)
        
        # Create title label
        title_label = QLabel(" اي بي تي في عربي")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        title_label.setFont(QFont('Arial', 32, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1565C0;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Arab Media Platform")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        subtitle_label.setFont(QFont('Arial', 18))
        subtitle_label.setStyleSheet("color: #757575;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #E0E0E0;")
        separator.setFixedHeight(2)
        layout.addWidget(separator)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont('Arial', 12))
        
        # Create Radio Tab
        radio_tab = QWidget()
        radio_layout = QVBoxLayout(radio_tab)
        radio_layout.setSpacing(20)
        radio_layout.setContentsMargins(15, 15, 15, 15)
        
        # Radio stations with categories
        self.radio_stations = {
            "الإذاعات التونسية الوطنية | National Tunisian Radio": {
                "Radio Tunis": "http://rtstream.tanitweb.com/nationale",
                "Radio Jeunes": "http://rtstream.tanitweb.com/jeunes",
                "RTCI": "http://rtstream.tanitweb.com/rtci",
                "Radio Culture": "http://rtstream.tanitweb.com/culture",
            },
            "الإذاعات الجهوية | Regional Radio": {
                "Radio Sfax": "http://rtstream.tanitweb.com/sfax",
                "Radio Monastir": "http://rtstream.tanitweb.com/monastir",
                "Radio Gafsa": "http://rtstream.tanitweb.com/gafsa",
            },
            "الإذاعات الخاصة | Private Radio": {
                "Mosaique FM": "https://radio.mosaiquefm.net/mosalive",
                "Express FM": "https://expressfm.ice.infomaniak.ch/expressfm-64.mp3",
                "Shems FM": "https://radio.shemsfm.net/shems",
            }
        }
        
        # Create scrollable radio section
        radio_scroll = QScrollArea()
        radio_scroll.setWidgetResizable(True)
        radio_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        radio_content = QWidget()
        radio_content_layout = QVBoxLayout(radio_content)
        radio_content_layout.setSpacing(20)
        radio_content_layout.setContentsMargins(10, 10, 10, 10)
        
        for category, stations in self.radio_stations.items():
            category_widget = CategoryWidget(category)
            for i, (name, url) in enumerate(stations.items()):
                station_button = CustomButton(name)
                station_button.clicked.connect(lambda checked, n=name, u=url: self.play_radio(n, u))
                category_widget.content_layout.addWidget(station_button, i // 2, i % 2)
            radio_content_layout.addWidget(category_widget)
        
        radio_scroll.setWidget(radio_content)
        radio_layout.addWidget(radio_scroll)
        
        # Create TV Tab
        tv_tab = QWidget()
        tv_tab.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        tv_layout = QHBoxLayout(tv_tab)  
        tv_layout.setSpacing(20)
        tv_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create left section for video player (40% of width)
        video_container = QWidget()
        video_container.setMinimumWidth(600)  
        video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        video_layout = QVBoxLayout(video_container)
        video_layout.setSpacing(15)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create video section
        video_section = QWidget()
        video_section.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        video_inner_layout = QVBoxLayout(video_section)
        video_inner_layout.setSpacing(15)
        video_inner_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add channel info label
        self.channel_info = QLabel("اختر قناة للمشاهدة | Select a channel to watch")
        self.channel_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.channel_info.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        self.channel_info.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #1976D2;
                padding: 15px;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        video_inner_layout.addWidget(self.channel_info)
        
        # Add video frame
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 4px solid #1976D2;
                border-radius: 15px;
                min-height: 450px;
            }
        """)
        self.video_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        video_inner_layout.addWidget(self.video_frame)
        
        # Add video controls
        video_controls = QWidget()
        video_controls.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        controls_layout = QHBoxLayout(video_controls)
        controls_layout.setSpacing(20)
        controls_layout.setContentsMargins(15, 10, 15, 10)
        
        volume_label = QLabel("مستوى الصوت | Volume")
        volume_label.setFont(QFont('Arial', 12))
        volume_label.setStyleSheet("color: white;")
        controls_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 10px;
                background: #3a3a3a;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #1976D2;
                border: none;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #1565C0;
            }
        """)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)
        
        self.fullscreen_button = CustomButton("ملء الشاشة | Fullscreen", is_control=True)
        self.fullscreen_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        controls_layout.addWidget(self.fullscreen_button)
        
        video_inner_layout.addWidget(video_controls)
        video_layout.addWidget(video_section)
        
        # Create right section for channels (60% of width)
        channels_container = QWidget()
        channels_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        channels_layout = QVBoxLayout(channels_container)
        channels_layout.setSpacing(0)
        channels_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title for channels section
        channels_title = QLabel("القنوات المتوفرة | Available Channels")
        channels_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        channels_title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        channels_title.setStyleSheet("""
            QLabel {
                color: #1976D2;
                padding: 10px;
                background-color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        channels_layout.addWidget(channels_title)
        
        # Create scrollable TV channels section
        tv_scroll = QScrollArea()
        tv_scroll.setWidgetResizable(True)
        tv_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #1976D2;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        tv_content = QWidget()
        tv_content.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
            }
        """)
        tv_content_layout = QVBoxLayout(tv_content)
        tv_content_layout.setSpacing(15)
        tv_content_layout.setContentsMargins(15, 15, 15, 15)
        
        # TV channels with categories and logos
        self.tv_channels = {
            "قنوات الأخبار العربية | Arabic News": {
                "Al Jazeera Live": {
                    "url": "https://live-hls-web-aja.getaj.net/AJA/index.m3u8",
                    "logo": "",
                    "description": "قناة الجزيرة الإخبارية المباشرة"
                },
                "Al Arabiya": {
                    "url": "https://live.alarabiya.net/alarabiapublish/alarabiya.smil/playlist.m3u8",
                    "logo": "",
                    "description": "قناة العربية الإخبارية"
                },
                "Sky News Arabia": {
                    "url": "https://stream.skynewsarabia.com/hls/sna.m3u8",
                    "logo": "",
                    "description": "سكاي نيوز عربية"
                },
            },
            "قنوات الأخبار الدولية | International News": {
                "France 24 Arabic": {
                    "url": "https://static.france24.com/live/F24_AR_HI_HLS/live_web.m3u8",
                    "logo": "",
                    "description": "فرانس 24 بالعربية"
                },
                "RT Arabic": {
                    "url": "https://rt-arb.rttv.com/live/rtarab/playlist.m3u8",
                    "logo": "",
                    "description": "روسيا اليوم"
                },
                "DW Arabic": {
                    "url": "https://dwamdstream103.akamaized.net/hls/live/2015526/dwstream103/index.m3u8",
                    "logo": "",
                    "description": "دويتشه فيله عربية"
                },
                "BBC Arabic": {
                    "url": "https://vs-hls-pushb-ww-live.akamaized.net/x=3/i=urn:bbc:pips:service:bbc_arabic_tv/pc_hd_abr_v2.m3u8",
                    "logo": "",
                    "description": "بي بي سي عربي"
                },
            },
            "قنوات إخبارية أخرى | Other News": {
                "Al Mayadeen": {
                    "url": "https://mdnlv.cdn.octivid.com/almdn/smil:mpegts.stream.smil/playlist.m3u8",
                    "logo": "",
                    "description": "قناة الميادين"
                },
                "Al Hiwar": {
                    "url": "https://mn-nl.mncdn.com/alhiwar_live/smil:alhiwar.smil/playlist.m3u8",
                    "logo": "",
                    "description": "قناة الحوار"
                },
                "Al Manar": {
                    "url": "https://manar.live/iptv/playlist.m3u8",
                    "logo": "",
                    "description": "قناة المنار"
                },
            }
        }
        
        for category, channels in self.tv_channels.items():
            category_widget = CategoryWidget(category)
            category_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border-radius: 12px;
                }
                QLabel {
                    color: #1976D2;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                }
            """)
            
            channels_grid = QGridLayout()
            channels_grid.setSpacing(10)
            
            row = 0
            col = 0
            for name, info in channels.items():
                channel_widget = QWidget()
                channel_widget.setStyleSheet("""
                    QWidget {
                        background-color: white;
                        border: 2px solid #E3F2FD;
                        border-radius: 10px;
                    }
                    QWidget:hover {
                        border-color: #1976D2;
                        background-color: #F5F9FF;
                    }
                """)
                channel_layout = QVBoxLayout(channel_widget)
                channel_layout.setSpacing(8)
                channel_layout.setContentsMargins(15, 15, 15, 15)
                
                # Channel header
                header_widget = QWidget()
                header_layout = QHBoxLayout(header_widget)
                header_layout.setSpacing(12)
                
                logo_label = QLabel(info['logo'])
                logo_label.setFont(QFont('Arial', 24))
                logo_label.setStyleSheet("color: #1976D2;")
                header_layout.addWidget(logo_label)
                
                name_label = QLabel(name)
                name_label.setFont(QFont('Arial', 13, QFont.Weight.Bold))
                name_label.setStyleSheet("color: #1976D2;")
                header_layout.addWidget(name_label)
                header_layout.addStretch()
                
                channel_layout.addWidget(header_widget)
                
                # Channel description
                desc_label = QLabel(info['description'])
                desc_label.setFont(QFont('Arial', 11))
                desc_label.setStyleSheet("color: #555;")
                desc_label.setWordWrap(True)
                desc_label.setMinimumHeight(40)
                channel_layout.addWidget(desc_label)
                
                # Watch button
                watch_button = CustomButton("مشاهدة | Watch")
                watch_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1976D2;
                        color: white;
                        border: none;
                        padding: 8px;
                        border-radius: 6px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1565C0;
                    }
                """)
                watch_button.clicked.connect(lambda checked, n=name, u=info['url']: self.play_tv(n, u))
                channel_layout.addWidget(watch_button)
                
                channels_grid.addWidget(channel_widget, row, col)
                
                col += 1
                if col >= 1:  
                    col = 0
                    row += 1
            
            category_widget.content_layout.addLayout(channels_grid, 0, 0)
            tv_content_layout.addWidget(category_widget)
        
        tv_scroll.setWidget(tv_content)
        channels_layout.addWidget(tv_scroll)
        
        # Add both sections to main layout
        tv_layout.addWidget(video_container, 40)  
        tv_layout.addWidget(channels_container, 60)  
        
        # Add tabs to tab widget
        self.tab_widget.addTab(radio_tab, "الراديو | Radio")
        self.tab_widget.addTab(tv_tab, "التلفاز | TV")
        layout.addWidget(self.tab_widget)
        
        # Create control panel
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 15px;
            }
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add status label to control panel
        self.status_label = QLabel("جاهز للتشغيل | Ready to Play")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont('Arial', 14))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #424242;
                padding: 10px;
            }
        """)
        control_layout.addWidget(self.status_label)
        
        # Add buttons to control panel
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(20)
        
        self.play_button = CustomButton("تشغيل | Play", is_control=True)
        self.stop_button = CustomButton("إيقاف | Stop", is_control=True)
        
        self.play_button.clicked.connect(self.resume_playback)
        self.stop_button.clicked.connect(self.stop_playback)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addStretch()
        
        control_layout.addWidget(buttons_widget)
        layout.addWidget(control_panel)
        
        # Style the window
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #666;
                padding: 12px 40px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f8f9fa;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #2196F3;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        
        # Create timer for status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  
        
    def play_radio(self, name, url):
        self.stop_playback()
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.play()
        self.current_media = name
        self.status_label.setText(f"يتم تشغيل الراديو | Playing Radio: {name}")
        
        # Hide fullscreen button for radio
        self.fullscreen_button.hide()
        
    def play_tv(self, name, url):
        self.stop_playback()
        media = self.instance.media_new(url)
        self.player.set_media(media)
        
        # Set the video output to the frame
        if sys.platform.startswith('linux'):
            self.player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_frame.winId()))
            
        self.player.play()
        self.current_media = name
        self.channel_info.setText(f"تشغيل: {name} | Playing: {name}")
        self.status_label.setText(f"يتم تشغيل القناة | Playing Channel: {name}")
        
        # Show fullscreen button only when playing TV
        self.fullscreen_button.show()
        
    def resume_playback(self):
        if self.current_media:
            self.player.play()
            self.status_label.setText(f"تم استئناف التشغيل | Resumed: {self.current_media}")
        
    def stop_playback(self):
        self.player.stop()
        self.status_label.setText("تم الإيقاف | Stopped")
        
    def update_status(self):
        if self.player.is_playing():
            # Update any status information if needed
            pass
        
    def on_tab_change(self, index):
        self.stop_playback()
        if index == 1:  # TV tab
            self.video_frame.show()
            self.fullscreen_button.show()
        else:
            self.video_frame.hide()
            self.fullscreen_button.hide()
            if self.video_frame.isFullScreen():
                self.toggle_fullscreen()
                
    def toggle_fullscreen(self):
        if self.video_frame.isFullScreen():
            # Exit fullscreen
            self.video_frame.showNormal()
            self.fullscreen_button.setText("ملء الشاشة | Fullscreen")
            # Show main window
            self.showNormal()
            # Restore video frame to its container
            self.video_frame.setParent(self.findChild(QWidget, "video_section"))
            self.video_frame.setStyleSheet("""
                QFrame {
                    background-color: #000000;
                    border: 4px solid #1976D2;
                    border-radius: 15px;
                    min-height: 450px;
                }
            """)
        else:
            # Enter fullscreen
            self.video_frame.setParent(None)  # Remove from current parent
            self.video_frame.setStyleSheet("""
                QFrame {
                    background-color: #000000;
                    border: none;
                }
            """)
            self.video_frame.showFullScreen()
            self.fullscreen_button.setText("إنهاء ملء الشاشة | Exit Fullscreen")
            
    def keyPressEvent(self, event):
        # Handle Escape key to exit fullscreen
        if event.key() == Qt.Key.Key_Escape and self.video_frame.isFullScreen():
            self.toggle_fullscreen()
        super().keyPressEvent(event)
        
    def closeEvent(self, event):
        self.player.stop()
        self.status_timer.stop()
        event.accept()
        
    def set_volume(self, value):
        self.player.audio_set_volume(value)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont('Arial', 11))
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MediaPlayer()
    window.show()
    sys.exit(app.exec())
