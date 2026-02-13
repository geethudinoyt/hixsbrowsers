import sys
import os
import json
import re
import warnings
from urllib.parse import urlparse, quote

# Suppress deprecation warnings for PyQt5
warnings.filterwarnings('ignore', category=DeprecationWarning)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QLineEdit, QPushButton, QToolBar, QTabWidget, 
                            QStatusBar, QProgressBar, QLabel, QHBoxLayout, 
                            QMenu, QAction, QFileDialog, QMessageBox, QShortcut,
                            QInputDialog, QDialog, QVBoxLayout, QDialogButtonBox)
from PyQt5.QtPrintSupport import QPrintDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt5.QtCore import QUrl, Qt, QTimer, pyqtSignal, QSettings, QStandardPaths
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QPixmap, QPainter, QCursor
from PyQt5.QtNetwork import QNetworkRequest

# Search engines configuration
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Yahoo": "https://search.yahoo.com/search?p=",
    "Startpage": "https://www.startpage.com/do/search?query=",
    "Yandex": "https://yandex.com/search/?text="
}

# Ad and tracker blocking patterns
AD_BLOCK_PATTERNS = [
    r".*\.doubleclick\.net",
    r".*\.googlesyndication\.com",
    r".*\.googleadservices\.com",
    r".*\.facebook\.com/tr.*",
    r".*\.facebook\.net.*\.js",
    r".*\.amazon-adsystem\.com",
    r".*\.adnxs\.com",
    r".*\.adsrvr\.org",
    r".*\.adform\.net",
    r".*\.criteo\.com",
    r".*\.taboola\.com",
    r".*\.outbrain\.com",
    r".*\.scorecardresearch\.com",
    r".*\.quantserve\.com",
    r".*\.quantcount\.com",
    r".*\.omtrdc\.net",
    r".*\.2mdn\.net",
    r".*\.admob\.com",
    r".*\.adservice\.google\.com",
    r".*pagead.*",
    r".*\.adtech.*",
    r".*\.advertising\.com",
    r".*\.tracking.*",
    r".*\.analytics.*",
    r".*\.telemetry.*",
    r".*\.metrics.*"
]

# Compile patterns for performance
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in AD_BLOCK_PATTERNS]

# Dark mode CSS to inject into websites
DARK_MODE_CSS = """
html {
    filter: invert(1) hue-rotate(180deg) !important;
    background-color: #111 !important;
}
img, video, canvas, svg, [style*="background-image"] {
    filter: invert(1) hue-rotate(180deg) !important;
}
iframe {
    filter: invert(1) hue-rotate(180deg) !important;
}
"""


class DownloadManager:
    """Manages file downloads - Chrome-like behavior"""
    def __init__(self, browser_window):
        self.browser_window = browser_window
        self.active_downloads = {}
        
    def handle_download_request(self, download_item):
        """Handle download request - auto-save to default location"""
        try:
            # Get download URL and suggested filename
            url = download_item.url().toString()
            suggested_name = download_item.downloadFileName()
            
            if not suggested_name:
                # Generate filename from URL
                suggested_name = url.split('/')[-1]
                if not suggested_name or '.' not in suggested_name:
                    suggested_name = "download"
            
            # Get default downloads folder
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(downloads_path):
                downloads_path = os.path.dirname(os.path.abspath(__file__))
            
            # Set download path
            download_item.setDownloadDirectory(downloads_path)
            download_item.setDownloadFileName(suggested_name)
            download_item.accept()
            
            # Update status
            self.browser_window.status_label.setText(f"Downloading: {suggested_name}")
            
            # Connect progress signal
            download_item.downloadProgress.connect(lambda r, t: self.on_progress(download_item, r, t))
            download_item.finished.connect(lambda: self.on_finished(download_item))
            
        except Exception as e:
            print(f"Download error: {e}")
            # Fallback - just accept without dialog
            try:
                download_item.accept()
            except:
                pass
    
    def on_progress(self, download_item, received, total):
        """Handle download progress"""
        try:
            if total > 0:
                percent = int((received / total) * 100)
                name = download_item.downloadFileName()
                received_mb = received / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                self.browser_window.status_label.setText(f"Downloading: {name} ({percent}% - {received_mb:.1f}/{total_mb:.1f} MB)")
        except:
            pass
    
    def on_finished(self, download_item):
        """Handle download completion"""
        try:
            name = download_item.downloadFileName()
            path = download_item.downloadDirectory()
            full_path = os.path.join(path, name)
            self.browser_window.status_label.setText(f"Download complete: {name}")
            
            # Show notification
            QMessageBox.information(
                self.browser_window,
                "Download Complete",
                f"File downloaded successfully:\n{full_path}"
            )
        except Exception as e:
            print(f"Download finish error: {e}")

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable all modern web features
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        self.settings().setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        # Enable smooth scrolling
        self.settings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        # Allow custom URL schemes
        self.settings().setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        self.settings().setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        
        self.tracker_count = 0
        self.dark_mode_enabled = False
        
        # Set up page permissions for camera/microphone
        try:
            self.page().profile().setPermissionRequestCallback(self.handle_permission_request)
        except:
            pass  # Some Qt versions don't support this
        
    def handle_permission_request(self, web_auth_exclusive, web_auth_urls, permission_type, callback):
        """Handle permission requests for camera, microphone, etc."""
        try:
            callback(QWebEnginePage.PermissionGrantedByUser)
        except:
            pass
    
    def set_dark_mode(self, enabled):
        """Inject or remove dark mode CSS"""
        self.dark_mode_enabled = enabled
        try:
            if enabled:
                # Inject dark mode CSS as a style element
                js_code = """
                (function() {
                    if (document.getElementById('hixs-dark-mode')) return;
                    var style = document.createElement('style');
                    style.id = 'hixs-dark-mode';
                    style.innerHTML = 'html { filter: invert(1) hue-rotate(180deg) !important; background-color: #111 !important; } img, video, canvas, svg, iframe { filter: invert(1) hue-rotate(180deg) !important; }';
                    document.head.appendChild(style);
                })();
                """
                self.page().runJavaScript(js_code)
            else:
                # Remove dark mode by removing the style element
                js_code = """
                (function() {
                    var style = document.getElementById('hixs-dark-mode');
                    if (style) style.remove();
                    document.documentElement.style.filter = '';
                    document.documentElement.style.backgroundColor = '';
                })();
                """
                self.page().runJavaScript(js_code)
        except Exception as e:
            pass  # Ignore JavaScript errors
    
    def contextMenuEvent(self, event):
        """Custom context menu"""
        try:
            menu = QMenu(self)
            
            # Get selected text
            selected_text = self.selectedText()
            
            # Copy/Paste
            copy_action = menu.addAction("Copy")
            copy_action.triggered.connect(self.copy)
            
            paste_action = menu.addAction("Paste")
            paste_action.triggered.connect(self.paste)
            
            menu.addSeparator()
            
            # Select all
            select_all_action = menu.addAction("Select All")
            select_all_action.triggered.connect(self.selectAll)
            
            if selected_text:
                menu.addSeparator()
                # Search selected text
                search_action = menu.addAction(f"Search: {selected_text[:30]}...")
                search_action.triggered.connect(lambda: self.parent().search_selected_text(selected_text))
            
            menu.exec_(event.globalPos())
        except Exception:
            pass  # Ignore context menu errors
    
    def createWindow(self, window_type):
        """Handle new window requests (popups)"""
        return self.parent().create_new_tab()

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, browser_window):
        super().__init__()
        self.browser_window = browser_window
        
    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            for pattern in COMPILED_PATTERNS:
                if pattern.match(url):
                    info.block(True)
                    self.browser_window.increment_tracker_count()
                    return
        except Exception:
            pass  # Ignore interception errors

class ModernWebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hixs Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        # Settings
        self.settings = QSettings("HixsBrowser", "HixsBrowser")
        self.current_search_engine = self.settings.value("search_engine", "Google")
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.ad_block_enabled = self.settings.value("ad_block_enabled", True, type=bool)
        self.tracker_count = 0
        
        # Set application style
        self.apply_theme()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tabs)
        
        # Create status bar
        self.create_status_bar()
        
        # Create shortcuts
        self.create_shortcuts()
        
        # Add first tab
        self.add_new_tab()
        
        # Initialize navigation buttons
        QTimer.singleShot(200, self.update_navigation_buttons)
        
        # Initialize download manager
        self.download_manager = DownloadManager(self)
        
        # Set window icon (create a simple icon)
        self.set_window_icon()
        
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Navigation buttons
        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("Back (Alt+Left Arrow)")
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.setToolTip("Forward (Alt+Right Arrow)")
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_btn)
        
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setToolTip("Reload (F5)")
        self.reload_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(self.reload_btn)
        
        self.stop_btn = QPushButton("✕")
        self.stop_btn.setToolTip("Stop (Esc)")
        self.stop_btn.clicked.connect(self.stop_loading)
        toolbar.addWidget(self.stop_btn)
        
        self.home_btn = QPushButton("⌂")
        self.home_btn.setToolTip("Home (Alt+Home)")
        self.home_btn.clicked.connect(self.go_home)
        toolbar.addWidget(self.home_btn)
        
        toolbar.addSeparator()
        
        # URL bar with search
        url_container = QWidget()
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(2)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        url_layout.addWidget(self.url_bar)
        
        # Search button
        search_btn = QPushButton("🔍")
        search_btn.setToolTip("Search")
        search_btn.clicked.connect(self.navigate_to_url)
        search_btn.setMaximumWidth(30)
        url_layout.addWidget(search_btn)
        
        toolbar.addWidget(url_container)
        
        toolbar.addSeparator()
        
        # Zoom controls
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.setMaximumWidth(25)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(40)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        toolbar.addWidget(self.zoom_label)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_btn.setMaximumWidth(25)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_btn)
        
        toolbar.addSeparator()
        
        # Search engine selector
        self.search_engine_btn = QPushButton("🔎 " + self.current_search_engine)
        self.search_engine_btn.setToolTip("Select Search Engine")
        self.search_engine_btn.clicked.connect(self.show_search_engine_menu)
        toolbar.addWidget(self.search_engine_btn)
        
        # Privacy indicator
        self.privacy_btn = QPushButton("🛡️")
        self.privacy_btn.setToolTip("Privacy Dashboard")
        self.privacy_btn.clicked.connect(self.show_privacy_dashboard)
        toolbar.addWidget(self.privacy_btn)
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙" if not self.dark_mode else "☀️")
        self.theme_btn.setToolTip("Toggle Dark/Light Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_btn)
        
        toolbar.addSeparator()
        
        # New tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setToolTip("New Tab (Ctrl+T)")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        toolbar.addWidget(new_tab_btn)
        
        # About button
        about_btn = QPushButton("?")
        about_btn.setToolTip("About Hixs Browser")
        about_btn.clicked.connect(self.show_about)
        toolbar.addWidget(about_btn)
        
        # Menu button
        menu_btn = QPushButton("⋮")
        menu_btn.setToolTip("Menu")
        menu_btn.clicked.connect(self.show_menu)
        toolbar.addWidget(menu_btn)
        
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Tracker count label
        self.tracker_label = QLabel("🛡️ 0 blocked")
        self.tracker_label.setToolTip("Trackers blocked this session")
        self.status_bar.addPermanentWidget(self.tracker_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
    def create_shortcuts(self):
        # Navigation shortcuts
        QShortcut(QKeySequence(Qt.Key_Left + Qt.AltModifier), self, self.go_back)
        QShortcut(QKeySequence(Qt.Key_Right + Qt.AltModifier), self, self.go_forward)
        QShortcut(QKeySequence(Qt.Key_F5), self, self.reload_page)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.stop_loading)
        QShortcut(QKeySequence(Qt.Key_Home + Qt.AltModifier), self, self.go_home)
        
        # Tab shortcuts
        QShortcut(QKeySequence(Qt.Key_T + Qt.ControlModifier), self, lambda: self.add_new_tab())
        QShortcut(QKeySequence(Qt.Key_W + Qt.ControlModifier), self, self.close_current_tab)
        QShortcut(QKeySequence(Qt.Key_Tab + Qt.ControlModifier), self, self.next_tab)
        QShortcut(QKeySequence(Qt.Key_Tab + Qt.ControlModifier + Qt.ShiftModifier), self, self.previous_tab)
        
        # File shortcuts
        QShortcut(QKeySequence(Qt.Key_O + Qt.ControlModifier), self, self.open_file)
        QShortcut(QKeySequence(Qt.Key_S + Qt.ControlModifier), self, self.save_page)
        QShortcut(QKeySequence(Qt.Key_P + Qt.ControlModifier), self, self.print_page)
        QShortcut(QKeySequence(Qt.Key_U + Qt.ControlModifier), self, self.view_page_source)
        
        # Search shortcut
        QShortcut(QKeySequence(Qt.Key_F + Qt.ControlModifier), self, self.find_in_page)
        
        # Zoom shortcuts
        QShortcut(QKeySequence(Qt.Key_Plus + Qt.ControlModifier), self, self.zoom_in)
        QShortcut(QKeySequence(Qt.Key_Equal + Qt.ControlModifier), self, self.zoom_in)
        QShortcut(QKeySequence(Qt.Key_Minus + Qt.ControlModifier), self, self.zoom_out)
        QShortcut(QKeySequence(Qt.Key_0 + Qt.ControlModifier), self, self.reset_zoom)
        
    def set_window_icon(self):
        """Set the window icon"""
        try:
            # Try to load the logo.jpeg file
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # Scale to appropriate size
                    pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.setWindowIcon(QIcon(pixmap))
                    return
            
            # Fallback: Create a simple icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(Qt.blue)
            painter.drawEllipse(4, 4, 24, 24)
            painter.setBrush(Qt.white)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "H")
            painter.end()
            icon = QIcon(pixmap)
            self.setWindowIcon(icon)
        except Exception as e:
            pass  # Ignore icon errors
        
    def add_new_tab(self, url=None):
        # Create browser tab
        browser = BrowserTab(self)
        
        if url is None:
            # Use custom homepage
            self.load_homepage(browser.page())
        else:
            # Handle hixs://home URL
            if url == "hixs://home":
                self.load_homepage(browser.page())
            else:
                browser.setUrl(QUrl(url))
        
        # Set up ad blocking if enabled
        if self.ad_block_enabled:
            try:
                interceptor = AdBlockInterceptor(self)
                browser.page().profile().setUrlRequestInterceptor(interceptor)
            except:
                pass
        
        # Set up download manager
        try:
            download_path = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)
            if download_path:
                browser.page().profile().setDownloadPath(download_path[0])
        except:
            pass  # Use default download location
        browser.page().profile().downloadRequested.connect(self.handle_download)
        
        # Apply dark mode if enabled
        if self.dark_mode:
            browser.dark_mode_enabled = True
        
        # Connect signals
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_urlbar(qurl, b))
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)
        browser.titleChanged.connect(lambda title, i=self.tabs.count(), b=browser: self.update_tab_title(i, title, b))
        
        # Add tab
        i = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(i)
        
        return browser
        
    def create_new_tab(self):
        return self.add_new_tab()
        
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
            
    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)
        
    def next_tab(self):
        current = self.tabs.currentIndex()
        next_index = (current + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(next_index)
        
    def previous_tab(self):
        current = self.tabs.currentIndex()
        prev_index = (current - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(prev_index)
        
    def on_tab_changed(self, index):
        """Handle tab change"""
        try:
            if index >= 0:
                browser = self.tabs.widget(index)
                if browser:
                    self.update_urlbar(browser.url(), browser)
                    self.update_navigation_buttons()
        except Exception:
            pass  # Ignore errors
                
    def update_navigation_buttons(self):
        """Update back/forward button states based on history"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                self.back_btn.setEnabled(current_browser.history().canGoBack())
                self.forward_btn.setEnabled(current_browser.history().canGoForward())
        except Exception:
            pass  # Ignore errors
                
    def navigate_to_url(self):
        """Navigate to URL entered in the address bar"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                url_text = self.url_bar.text().strip()
                if url_text:
                    url = self.process_url_input(url_text)
                    # Handle hixs://home URL scheme
                    if url == "hixs://home":
                        self.load_homepage(current_browser.page())
                        return
                    current_browser.setUrl(QUrl(url))
                else:
                    # If empty, go to homepage
                    self.load_homepage(current_browser.page())
        except Exception:
            pass  # Ignore errors
            
    def process_url_input(self, url_text):
        """Smart URL detection - distinguishes between URLs and search queries"""
        
        # Handle empty input
        if not url_text:
            return self.get_homepage()
        
        # Check for protocol - handle directly
        if url_text.startswith(("http://", "https://", "file://", "ftp://", "mailto:")):
            return url_text
        
        # Check for valid IP address (including with port)
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
        if re.match(ip_pattern, url_text):
            return f"http://{url_text}"
        
        # Check for localhost
        if url_text.lower().startswith(("localhost", "127.0.0.1", "0.0.0.0")):
            return f"http://{url_text}"
        
        # Check if it's a search query (contains spaces or common search patterns)
        if " " in url_text or url_text.startswith("?") or url_text.startswith("!"):
            # This is likely a search query
            search_engine = SEARCH_ENGINES.get(self.current_search_engine, SEARCH_ENGINES["Google"])
            # URL encode the query properly
            encoded_query = quote(url_text, safe='')
            return f"{search_engine}{encoded_query}"
        
        # Check if it looks like a domain (contains a dot)
        if "." in url_text:
            # Check if it's a valid domain format
            domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z]{2,})+$'
            if re.match(domain_pattern, url_text):
                return f"https://{url_text}"
            # Maybe it's a single-word domain like "localhost" or "test"
            if re.match(r'^[a-zA-Z0-9-]+$', url_text):
                return f"https://{url_text}"
            # Could be a domain with path
            if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z]{2,})', url_text):
                return f"https://{url_text}"
        
        # Default: treat as search query
        search_engine = SEARCH_ENGINES.get(self.current_search_engine, SEARCH_ENGINES["Google"])
        encoded_query = quote(url_text, safe='')
        return f"{search_engine}{encoded_query}"
    
    def get_homepage(self):
        """Returns the default homepage URL - use custom local page"""
        return "hixs://home"
            
    def update_urlbar(self, qurl, browser=None):
        """Update the URL bar with current page URL"""
        try:
            if browser == self.tabs.currentWidget():
                url = qurl.toString()
                self.url_bar.setText(url)
                self.url_bar.setCursorPosition(0)
        except Exception:
            pass  # Ignore errors
            
    def update_tab_title(self, index, title, browser):
        """Update tab title"""
        try:
            if browser == self.tabs.widget(index):
                # Truncate long titles
                if len(title) > 30:
                    title = title[:27] + "..."
                self.tabs.setTabText(index, title or "Untitled")
        except Exception:
            pass  # Ignore errors
            
    def on_load_started(self):
        """Handle page load start"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Loading...")
            self.reload_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            
            # Update window title
            self.setWindowTitle("Loading... - Hixs Browser")
        except Exception:
            pass  # Ignore errors
        
    def on_load_progress(self, progress):
        """Handle page load progress"""
        try:
            self.progress_bar.setValue(progress)
        except Exception:
            pass  # Ignore errors
        
    def on_load_finished(self, success):
        self.progress_bar.setVisible(False)
        self.reload_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        
        # Update window title
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                title = current_browser.page().title()
                if title:
                    self.setWindowTitle(f"{title} - Hixs Browser")
                else:
                    self.setWindowTitle("Hixs Browser")
        except Exception:
            self.setWindowTitle("Hixs Browser")
        
        if success:
            self.status_label.setText("Done")
            # Apply dark mode to page if enabled
            if self.dark_mode:
                QTimer.singleShot(500, lambda: self.apply_dark_mode_to_current_tab())
        else:
            self.status_label.setText("Failed to load page")
            # Try to reload once on failure
            QTimer.singleShot(1000, lambda: self.reload_page() if not success else None)
            
        # Update current tab title
        if current_browser:
            title = current_browser.page().title()
            current_index = self.tabs.currentIndex()
            self.update_tab_title(current_index, title, current_browser)
        
        # Update zoom label
        if current_browser:
            self.update_zoom_label(current_browser.zoomFactor())
    
    def apply_dark_mode_to_current_tab(self):
        """Apply dark mode CSS to the current tab"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser and hasattr(current_browser, 'set_dark_mode'):
                current_browser.set_dark_mode(self.dark_mode)
        except Exception:
            pass  # Ignore errors
    
    def apply_dark_mode_to_all_tabs(self):
        """Apply dark mode CSS to all open tabs"""
        try:
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if browser and hasattr(browser, 'set_dark_mode'):
                    browser.set_dark_mode(self.dark_mode)
        except Exception:
            pass  # Ignore errors
            
    def go_back(self):
        """Go back in history"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                # Check if we can go back
                if current_browser.history().canGoBack():
                    current_browser.back()
                # Update button states after navigation
                QTimer.singleShot(100, self.update_navigation_buttons)
        except Exception as e:
            print(f"Back error: {e}")
            pass
            
    def go_forward(self):
        """Go forward in history"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                # Check if we can go forward
                if current_browser.history().canGoForward():
                    current_browser.forward()
                # Update button states after navigation
                QTimer.singleShot(100, self.update_navigation_buttons)
        except Exception as e:
            print(f"Forward error: {e}")
            pass
            
    def reload_page(self):
        """Reload the current page"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                current_browser.reload()
        except Exception:
            pass  # Ignore errors
            
    def stop_loading(self):
        """Stop page loading"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                current_browser.stop()
        except Exception:
            pass  # Ignore errors
            
    def go_home(self):
        """Go to homepage"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                self.load_homepage(current_browser.page())
        except Exception:
            pass  # Ignore errors
            
    def show_menu(self):
        menu = QMenu(self)
        
        # File menu
        file_menu = menu.addMenu("File")
        file_menu.addAction("New Tab", lambda: self.add_new_tab(), QKeySequence(Qt.Key_T + Qt.ControlModifier))
        file_menu.addAction("Close Tab", self.close_current_tab, QKeySequence(Qt.Key_W + Qt.ControlModifier))
        file_menu.addSeparator()
        file_menu.addAction("Open File...", self.open_file, QKeySequence(Qt.Key_O + Qt.ControlModifier))
        file_menu.addAction("Save Page As...", self.save_page, QKeySequence(Qt.Key_S + Qt.ControlModifier))
        file_menu.addAction("View Page Source", self.view_page_source, QKeySequence(Qt.Key_U + Qt.ControlModifier))
        file_menu.addSeparator()
        file_menu.addAction("Print...", self.print_page, QKeySequence(Qt.Key_P + Qt.ControlModifier))
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menu.addMenu("Edit")
        edit_menu.addAction("Find in Page", self.find_in_page, QKeySequence(Qt.Key_F + Qt.ControlModifier))
        edit_menu.addAction("Copy URL", self.copy_url)
        
        # View menu
        view_menu = menu.addMenu("View")
        view_menu.addAction("Zoom In", self.zoom_in, QKeySequence(Qt.Key_Plus + Qt.ControlModifier))
        view_menu.addAction("Zoom Out", self.zoom_out, QKeySequence(Qt.Key_Minus + Qt.ControlModifier))
        view_menu.addAction("Reset Zoom", self.reset_zoom, QKeySequence(Qt.Key_0 + Qt.ControlModifier))
        view_menu.addSeparator()
        view_menu.addAction("Full Screen", self.toggle_full_screen, QKeySequence(Qt.Key_F11))
        
        # Privacy menu
        privacy_menu = menu.addMenu("🛡️ Privacy")
        privacy_menu.addAction("Privacy Dashboard", self.show_privacy_dashboard)
        ad_block_action = QAction("Ad Blocking", self)
        ad_block_action.setCheckable(True)
        ad_block_action.setChecked(self.ad_block_enabled)
        ad_block_action.triggered.connect(self.toggle_ad_blocking)
        privacy_menu.addAction(ad_block_action)
        
        # Force dark mode on websites option
        self.force_dark_website = self.settings.value("force_dark_website", False, type=bool)
        force_dark_action = QAction("Force Dark Mode on Websites", self)
        force_dark_action.setCheckable(True)
        force_dark_action.setChecked(self.force_dark_website)
        force_dark_action.triggered.connect(self.toggle_force_dark_website)
        privacy_menu.addAction(force_dark_action)
        
        # Search menu
        search_menu = menu.addMenu("🔍 Search Engine")
        for engine_name in SEARCH_ENGINES.keys():
            action = QAction(engine_name, self)
            action.setCheckable(True)
            action.setChecked(engine_name == self.current_search_engine)
            action.triggered.connect(lambda checked, name=engine_name: self.set_search_engine(name))
            search_menu.addAction(action)
        
        # Theme menu
        theme_menu = menu.addMenu("🎨 Theme")
        light_action = QAction("Light Mode", self)
        light_action.setCheckable(True)
        light_action.setChecked(not self.dark_mode)
        light_action.triggered.connect(lambda: self.set_theme(False))
        theme_menu.addAction(light_action)
        dark_action = QAction("Dark Mode", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(self.dark_mode)
        dark_action.triggered.connect(lambda: self.set_theme(True))
        theme_menu.addAction(dark_action)
        
        # History menu
        history_menu = menu.addMenu("History")
        history_menu.addAction("Show History", self.show_history)
        history_menu.addAction("Clear History", self.clear_history)
        
        # Help menu
        help_menu = menu.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        
        # Show menu at cursor position
        cursor_pos = QCursor.pos()
        menu.exec_(cursor_pos)
        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                current_browser.setUrl(QUrl.fromLocalFile(file_path))
                
    def save_page(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Page As", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                current_browser.page().save(file_path)
                
    def find_in_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.page().findText("")
            
    def copy_url(self):
        """Copy current URL to clipboard"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                url = current_browser.url().toString()
                QApplication.clipboard().setText(url)
        except Exception:
            pass  # Ignore errors
            
    def search_selected_text(self, text):
        """Search for selected text using current search engine"""
        try:
            if text:
                search_url = f"{SEARCH_ENGINES.get(self.current_search_engine, SEARCH_ENGINES['Google'])}{quote(text, safe='')}"
                current_browser = self.tabs.currentWidget()
                if current_browser:
                    current_browser.setUrl(QUrl(search_url))
        except Exception:
            pass  # Ignore errors
    
    def view_page_source(self):
        """View the page source in a new tab"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            url = current_browser.url().toString()
            if url:
                # Open view-source URL
                self.add_new_tab(f"view-source:{url}")
            
    def zoom_in(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(current_browser.zoomFactor() + 0.1)
            
    def zoom_out(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(current_browser.zoomFactor() - 0.1)
            
    def reset_zoom(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(1.0)
            
    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def show_history(self):
        QMessageBox.information(self, "History", "History feature coming soon!")
        
    def clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History", "Are you sure you want to clear browsing history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QWebEngineProfile.defaultProfile().clearAllVisitedLinks()
            QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")
            
    def show_about(self):
        QMessageBox.about(
            self, "About Hixs Browser",
            "<h2>Hixs Browser v2.1</h2>"
            "<p>A modern, privacy-focused web browser built with PyQt5.</p>"
            "<h3>Features:</h3>"
            "<ul>"
            "<li>Tabbed browsing with smooth switching</li>"
            "<li>Multi-engine search (Google, Bing, DuckDuckGo, etc.)</li>"
            "<li>Ad and tracker blocking</li>"
            "<li>Dark/Light theme support</li>"
            "<li>Smart URL detection</li>"
            "<li>Full keyboard shortcuts</li>"
            "<li>Modern web features support</li>"
            "<li>Download manager</li>"
            "<li>Print functionality</li>"
            "</ul>"
            "<hr>"
            "<p><b>Developed by:</b> geethudinoyt (ruthvik pedapondara)</p>"
            "<p><b>Powered by:</b> QtWebEngine (Chromium)</p>"
        )
        
    def handle_download(self, download_item):
        """Handle download requests from web pages"""
        self.download_manager.handle_download_request(download_item)
        
    # ==================== NEW FEATURES ====================
    
    def apply_theme(self):
        """Apply dark or light theme based on settings"""
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QToolBar {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 4px;
                    spacing: 2px;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 30px;
                    color: #ffffff;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    border-color: #5d5d5d;
                }
                QPushButton:pressed {
                    background-color: #2d2d2d;
                }
                QLineEdit {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 14px;
                    color: #ffffff;
                }
                QLineEdit:focus {
                    border-color: #4285f4;
                }
                QTabWidget::pane {
                    border: 1px solid #3d3d3d;
                    background-color: #1e1e1e;
                    border-radius: 4px;
                }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-bottom: none;
                    border-radius: 4px 4px 0 0;
                    padding: 8px 16px;
                    margin-right: 2px;
                    color: #cccccc;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    border-bottom: 1px solid #1e1e1e;
                    color: #ffffff;
                }
                QTabBar::tab:hover {
                    background-color: #3d3d3d;
                }
                QProgressBar {
                    border: none;
                    background-color: transparent;
                    height: 2px;
                }
                QProgressBar::chunk {
                    background-color: #4285f4;
                }
                QMenu {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                }
                QMenu::item:selected {
                    background-color: #4285f4;
                }
                QStatusBar {
                    background-color: #2d2d2d;
                    color: #cccccc;
                }
                QLabel {
                    color: #cccccc;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QToolBar {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 4px;
                    spacing: 2px;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 30px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    border-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #e8e8e8;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #4285f4;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background-color: #ffffff;
                    border-radius: 4px;
                }
                QTabBar::tab {
                    background-color: #f8f8f8;
                    border: 1px solid #e0e0e0;
                    border-bottom: none;
                    border-radius: 4px 4px 0 0;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 1px solid #ffffff;
                }
                QTabBar::tab:hover {
                    background-color: #f0f0f0;
                }
                QProgressBar {
                    border: none;
                    background-color: transparent;
                    height: 2px;
                }
                QProgressBar::chunk {
                    background-color: #4285f4;
                }
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                }
                QMenu::item:selected {
                    background-color: #f0f0f0;
                }
                QStatusBar {
                    background-color: #ffffff;
                }
            """)
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self.apply_theme()
        self.theme_btn.setText("🌙" if not self.dark_mode else "☀️")
        # Apply dark mode to all tabs
        self.apply_dark_mode_to_all_tabs()
    
    def show_search_engine_menu(self):
        """Show menu to select search engine"""
        menu = QMenu(self)
        
        for engine_name in SEARCH_ENGINES.keys():
            action = QAction(engine_name, self)
            action.setCheckable(True)
            action.setChecked(engine_name == self.current_search_engine)
            action.triggered.connect(lambda checked, name=engine_name: self.set_search_engine(name))
            menu.addAction(action)
        
        # Show menu at button position
        cursor_pos = QCursor.pos()
        menu.exec_(cursor_pos)
    
    def set_search_engine(self, engine_name):
        """Set the search engine"""
        self.current_search_engine = engine_name
        self.settings.setValue("search_engine", engine_name)
        self.search_engine_btn.setText("🔎 " + engine_name)
    
    def toggle_ad_blocking(self):
        """Toggle ad blocking on/off"""
        self.ad_block_enabled = not self.ad_block_enabled
        self.settings.setValue("ad_block_enabled", self.ad_block_enabled)
        QMessageBox.information(
            self, "Ad Blocking",
            f"Ad blocking has been {'enabled' if self.ad_block_enabled else 'disabled'}.\n\n"
            "Changes will take effect on newly opened tabs."
        )
    
    def toggle_force_dark_website(self):
        """Toggle forcing dark mode on all websites"""
        self.force_dark_website = not self.force_dark_website
        self.settings.setValue("force_dark_website", self.force_dark_website)
        # Apply to all current tabs
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser and hasattr(browser, 'set_dark_mode'):
                browser.set_dark_mode(self.force_dark_website)
        QMessageBox.information(
            self, "Force Dark Mode on Websites",
            f"Dark mode on websites is now {'enabled' if self.force_dark_website else 'disabled'}.\n\n"
            "This will apply to all open tabs."
        )
    
    def set_theme(self, dark):
        """Set the theme mode"""
        if self.dark_mode != dark:
            self.toggle_theme()
    
    def show_privacy_dashboard(self):
        """Show privacy dashboard with blocking statistics"""
        ad_block_status = "Enabled" if self.ad_block_enabled else "Disabled"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Privacy Dashboard")
        msg.setText("<h2>🛡️ Privacy Protection Status</h2>")
        msg.setInformativeText(
            f"<b>Trackers Blocked:</b> {self.tracker_count}<br><br>"
            f"<b>Ad Blocking:</b> {ad_block_status}<br><br>"
            f"<b>Current Search Engine:</b> {self.current_search_engine}<br><br>"
            f"<b>Theme:</b> {'Dark' if self.dark_mode else 'Light'}"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def increment_tracker_count(self):
        """Increment the tracker count when a tracker is blocked"""
        self.tracker_count += 1
        self.tracker_label.setText(f"🛡️ {self.tracker_count} blocked")
    
    def load_homepage(self, page: QWebEnginePage):
        """Load custom HTML homepage"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hixs Browser</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    animation: gradientBG 15s ease infinite;
                }
                @keyframes gradientBG {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
                .container {
                    text-align: center;
                    padding: 40px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    max-width: 600px;
                    width: 90%;
                    animation: fadeIn 0.8s ease-out;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                h1 {
                    color: #667eea;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }
                .tagline {
                    color: #666;
                    font-size: 1.1em;
                    margin-bottom: 30px;
                }
                .search-box {
                    width: 100%;
                    padding: 15px 25px;
                    font-size: 18px;
                    border: 2px solid #667eea;
                    border-radius: 50px;
                    outline: none;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
                }
                .search-box:focus {
                    border-color: #764ba2;
                    box-shadow: 0 4px 20px rgba(118, 75, 162, 0.3);
                }
                .shortcuts {
                    margin-top: 30px;
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    flex-wrap: wrap;
                }
                .shortcut {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 10px 15px;
                    background: #f5f5f5;
                    border-radius: 10px;
                    font-size: 14px;
                    color: #555;
                    transition: all 0.3s ease;
                }
                .shortcut:hover {
                    background: #667eea;
                    color: white;
                    transform: translateY(-2px);
                }
                .shortcut kbd {
                    background: #fff;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-family: monospace;
                    font-size: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .footer {
                    margin-top: 30px;
                    color: #888;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Hixs Browser</h1>
                <p class="tagline">Fast, Private, Secure Browsing</p>
                <input type="text" class="search-box" id="searchInput" 
                       placeholder="Search the web or enter a URL..." 
                       autofocus
                       onkeydown="if(event.key==='Enter'){window.location.href='hixs://search/'+encodeURIComponent(this.value)}">
                <div class="shortcuts">
                    <div class="shortcut"><kbd>Ctrl</kbd>+<kbd>T</kbd> New Tab</div>
                    <div class="shortcut"><kbd>Ctrl</kbd>+<kbd>W</kbd> Close Tab</div>
                    <div class="shortcut"><kbd>Ctrl</kbd>+<kbd>R</kbd> Refresh</div>
                    <div class="shortcut"><kbd>F11</kbd> Fullscreen</div>
                </div>
                <div class="footer">
                    Hixs Browser v2.1 • Privacy First<br>
                    Developed by: geethudinoyt (ruthvik pedapondara)
                </div>
            </div>
            <script>
                document.getElementById('searchInput').focus();
            </script>
        </body>
        </html>
        """
        page.setHtml(html)

    def zoom_in(self):
        """Zoom in"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                new_zoom = current_browser.zoomFactor() + 0.1
                current_browser.setZoomFactor(new_zoom)
                self.update_zoom_label(new_zoom)
        except Exception:
            pass  # Ignore errors
            
    def zoom_out(self):
        """Zoom out"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                new_zoom = current_browser.zoomFactor() - 0.1
                current_browser.setZoomFactor(new_zoom)
                self.update_zoom_label(new_zoom)
        except Exception:
            pass  # Ignore errors
            
    def reset_zoom(self):
        """Reset zoom to default"""
        try:
            current_browser = self.tabs.currentWidget()
            if current_browser:
                current_browser.setZoomFactor(1.0)
                self.update_zoom_label(1.0)
        except Exception:
            pass  # Ignore errors
    
    def update_zoom_label(self, zoom_factor):
        """Update zoom level label"""
        percentage = int(zoom_factor * 100)
        self.zoom_label.setText(f"{percentage}%")
    
    def print_page(self):
        """Print the current page"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            from PyQt5.QtPrintSupport import QPrintDialog
            dialog = QPrintDialog(self)
            if dialog.exec_() == QPrintDialog.Accepted:
                current_browser.page().print(dialog.printer(), lambda success: None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application name and organization
    app.setApplicationName("Hixs Browser")
    app.setOrganizationName("Hixs Browser")
    
    # Set application icon for taskbar
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                app.setWindowIcon(QIcon(pixmap))
    except:
        pass
    
    # Create and show browser
    browser = ModernWebBrowser()
    browser.show()
    
    sys.exit(app.exec_())
