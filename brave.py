import sys
import os
import json
import re
import warnings
import threading
import time
from urllib.parse import urlparse, quote, unquote
from datetime import datetime

# Suppress deprecation warnings for PyQt5
warnings.filterwarnings('ignore', category=DeprecationWarning)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QLineEdit, QPushButton, QToolBar, QTabWidget,
                             QStatusBar, QProgressBar, QLabel, QHBoxLayout,
                             QMenu, QAction, QFileDialog, QMessageBox, QShortcut,
                             QInputDialog, QDialog, QDialogButtonBox, QFrame,
                             QListWidget, QListWidgetItem, QAbstractItemView,
                             QTreeWidget, QTreeWidgetItem, QHeaderView, QSplitter,
                             QTabBar, QStyle, QToolButton, QSizePolicy, QScrollArea,
                             QPlainTextEdit, QComboBox, QCheckBox, QGridLayout,
                             QGroupBox, QSlider, QSystemTrayIcon)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEngineSettings, 
                                      QWebEngineProfile, QWebEnginePage,
                                      QWebEngineDownloadItem)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt5.QtCore import (QUrl, Qt, QTimer, pyqtSignal, QSettings, QStandardPaths, 
                          QPoint, QSize, QEvent, QThread, QObject, QFile, QIODevice,
                          QByteArray, QDataStream)
from PyQt5.QtGui import (QIcon, QFont, QKeySequence, QPixmap, QPainter, QCursor, 
                         QColor, QPalette, QDesktopServices, QCloseEvent)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Search engines configuration - FIXED: removed trailing spaces
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Yahoo": "https://search.yahoo.com/search?p=",
    "Startpage": "https://www.startpage.com/do/search?query=",
    "Yandex": "https://yandex.com/search/?text=",
    "Baidu": "https://www.baidu.com/s?wd=",
    "Ecosia": "https://www.ecosia.org/search?q="
}

# Enhanced ad and tracker blocking patterns (Brave-like) - FIXED: removed duplicates
AD_BLOCK_PATTERNS = [
    r".*\.doubleclick\.net.*",
    r".*\.googlesyndication\.com.*",
    r".*\.googleadservices\.com.*",
    r".*\.facebook\.com/tr.*",
    r".*\.facebook\.net.*\.js",
    r".*\.amazon-adsystem\.com.*",
    r".*\.adnxs\.com.*",
    r".*\.adsrvr\.org.*",
    r".*\.adform\.net.*",
    r".*\.criteo\.com.*",
    r".*\.taboola\.(com|net|io|co\.uk|co\.il|com\.au|de|fr|it|jp|nl|pl|se|es|ca|com\.br|mx|ru).*",
    r".*\.outbrain\.com.*",
    r".*\.scorecardresearch\.com.*",
    r".*\.quantserve\.com.*",
    r".*\.quantcount\.com.*",
    r".*\.omtrdc\.net.*",
    r".*\.2mdn\.net.*",
    r".*\.admob\.com.*",
    r".*\.adservice\.google\.com.*",
    r".*pagead.*",
    r".*\.adtech\..*",
    r".*\.advertising\.com.*",
    r".*\.tracking\..*",
    r".*\.analytics\..*",
    r".*\.telemetry\..*",
    r".*\.metrics\..*",
    r".*\.google-analytics\.com.*",
    r".*\.hotjar\.com.*",
    r".*\.mixpanel\.com.*",
    r".*\.segment\.io.*",
    r".*\.amplitude\.com.*",
    r".*\.intercom\.io.*",
    r".*\.drift\.com.*",
    r".*\.zendesk\.com.*",
    r".*\.crisp\.chat.*",
    r".*\.tawk\.to.*",
    r".*\.livechatinc\.com.*",
    r".*\.olark\.com.*",
    r".*\.zopim\.com.*",
    r".*\.snapengage\.com.*",
    r".*\.purechat\.com.*",
    r".*\.userlike\.com.*",
    r".*\.smartsupp\.com.*",
    r".*\.jivosite\.com.*",
    r".*\.comm100\.com.*",
    r".*\.chatra\.io.*",
    r".*\.tido\.com.*",
    r".*\.gorgias\.com.*",
    r".*\.re\:amaze\.com.*",
    r".*\.help Scout\.com.*",
    r".*\.frontapp\.com.*",
    r".*\.kustomer\.com.*",
    r".*\.gladly\.com.*",
    r".*\.richpanel\.com.*",
    r".*\.chatwoot\.com.*",
    r".*\.chaskiq\.com.*",
    r".*\.papercups\.io.*",
    r".*\.widgetbot\.com.*",
    r".*\.carbon\.chat.*",
    r".*\.botstar\.com.*",
    r".*\.landbot\.io.*",
    r".*\.chatbot\.com.*",
    r".*\.intercom\.com.*",
    r".*\.hubspot\.com.*",
    r".*\.marketo\.com.*",
    r".*\.pardot\.com.*",
    r".*\.eloqua\.com.*",
    r".*\.mailchimp\.com.*",
    r".*\.constantcontact\.com.*",
    r".*\.sendgrid\.com.*",
    r".*\.twilio\.com.*",
    r".*\.nexmo\.com.*",
    r".*\.plivo\.com.*",
    r".*\.messagebird\.com.*",
    r".*\.textmagic\.com.*",
    r".*\.eztexting\.com.*",
    r".*\.slicktext\.com.*",
    r".*\.simpletexting\.com.*",
    r".*\.textedly\.com.*",
    r".*\.zipwhip\.com.*",
    r".*\.salesforce\.com.*",
    r".*\.zendesk\.com.*",
    r".*\.freshdesk\.com.*",
    r".*\.zoho\.com.*",
    r".*\.hubspot\.com.*",
    r".*\.pipedrive\.com.*",
    r".*\.salesloft\.com.*",
    r".*\.outreach\.io.*",
    r".*\.apollo\.io.*",
    r".*\.zoominfo\.com.*",
    r".*\.lusha\.com.*",
    r".*\.cognism\.com.*",
    r".*\.6sense\.com.*",
    r".*\.demandbase\.com.*",
    r".*\.terminus\.com.*",
    r".*\.rollworks\.com.*",
    r".*\.triblio\.com.*",
    r".*\.engagio\.com.*",
    r".*\.bizible\.com.*",
    r".*\.attribution\.com.*",
    r".*\.dreamdata\.io.*",
    r".*\.funnel\.io.*",
    r".*\.supermetrics\.com.*",
    r".*\.fivetran\.com.*",
    r".*\.stitchdata\.com.*",
    r".*\.segment\.com.*",
    r".*\.mparticle\.com.*",
    r".*\.tealium\.com.*",
    r".*\.ensighten\.com.*",
    r".*\.signal\.com.*",
    r".*\.tagcommander\.com.*",
    r".*\.commandersact\.com.*",
    r".*\.adobe\.com.*",
    r".*\.google\.com.*",
    r".*\.facebook\.com.*",
    r".*\.twitter\.com.*",
    r".*\.linkedin\.com.*",
    r".*\.pinterest\.com.*",
    r".*\.snapchat\.com.*",
    r".*\.tiktok\.com.*",
    r".*\.reddit\.com.*",
    r".*\.quora\.com.*",
    r".*\.medium\.com.*",
    r".*\.wordpress\.com.*",
    r".*\.blogger\.com.*",
    r".*\.tumblr\.com.*",
    r".*\.ghost\.org.*",
    r".*\.squarespace\.com.*",
    r".*\.wix\.com.*",
    r".*\.weebly\.com.*",
    r".*\.shopify\.com.*",
    r".*\.bigcommerce\.com.*",
    r".*\.magento\.com.*",
    r".*\.woocommerce\.com.*",
    r".*\.prestashop\.com.*",
    r".*\.opencart\.com.*",
    r".*\.drupal\.com.*",
    r".*\.joomla\.com.*",
    r".*\.typo3\.com.*",
    r".*\.contao\.com.*",
    r".*\.concrete5\.com.*",
    r".*\.modx\.com.*",
    r".*\.processwire\.com.*",
    r".*\.expressionengine\.com.*",
    r".*\.craftcms\.com.*",
    r".*\.statamic\.com.*",
    r".*\.octobercms\.com.*",
    r".*\.grav\.com.*",
    r".*\.getkirby\.com.*",
    r".*\.directus\.io.*",
    r".*\.strapi\.io.*",
    r".*\.contentful\.com.*",
    r".*\.prismic\.io.*",
    r".*\.sanity\.io.*",
    r".*\.dato\.com.*",
    r".*\.buttercms\.com.*",
    r".*\.cosmicjs\.com.*",
    r".*\.graphcms\.com.*",
    r".*\.kentico\.com.*",
    r".*\.umbraco\.com.*",
    r".*\.sitecore\.com.*",
    r".*\.episerver\.com.*",
    r".*\.optimizely\.com.*",
    r".*\.abtasty\.com.*",
    r".*\.vwo\.com.*",
    r".*\.convert\.com.*",
    r".*\.unbounce\.com.*",
    r".*\.instapage\.com.*",
    r".*\.leadpages\.com.*",
    r".*\.clickfunnels\.com.*",
    r".*\.kartra\.com.*",
    r".*\.kajabi\.com.*",
    r".*\.teachable\.com.*",
    r".*\.thinkific\.com.*",
    r".*\.podia\.com.*",
    r".*\.gumroad\.com.*",
    r".*\.stripe\.com.*",
    r".*\.paypal\.com.*",
    r".*\.braintree\.com.*",
    r".*\.square\.com.*",
    r".*\.adyen\.com.*",
    r".*\.checkout\.com.*",
    r".*\.worldpay\.com.*",
    r".*\.authorize\.net.*",
    r".*\.cybersource\.com.*",
    r".*\.sagepay\.com.*",
    r".*\.2checkout\.com.*",
    r".*\.paddle\.com.*",
    r".*\.fastspring\.com.*",
    r".*\.avangate\.com.*",
    r".*\.digitalriver\.com.*",
    r".*\.cleverbridge\.com.*",
    r".*\.shareit\.com.*",
    r".*\.element5\.com.*",
    r".*\.regnow\.com.*",
    r".*\.esellerate\.com.*",
    r".*\.kagi\.com.*",
    r".*\.fastmail\.com.*",
    r".*\.protonmail\.com.*",
    r".*\.tutanota\.com.*",
    r".*\.startmail\.com.*",
    r".*\.runbox\.com.*",
    r".*\.posteo\.com.*",
    r".*\.mailbox\.org.*",
    r".*\.kolabnow\.com.*",
    r".*\.mailfence\.com.*",
    r".*\.zoho\.com.*",
    r".*\.gmail\.com.*",
    r".*\.outlook\.com.*",
    r".*\.yahoo\.com.*",
    r".*\.aol\.com.*",
    r".*\.icloud\.com.*",
    r".*\.yandex\.com.*",
    r".*\.mail\.ru.*",
    r".*\.gmx\.com.*",
    r".*\.mail\.com.*",
    r".*\.hushmail\.com.*",
    r".*\.countermail\.com.*",
    r".*\.safemail\.com.*",
    r".*\.scryptmail\.com.*",
    r".*\.ctemplar\.com.*",
    r".*\.torbox\.com.*",
    r".*\.secmail\.pro.*",
    r".*\.dnmx\.org.*",
    r".*\.elude\.in.*",
    r".*\.cock\.li.*",
    r".*\.vfemail\.net.*",
    r".*\.mailnesia\.com.*",
    r".*\.guerrillamail\.com.*",
    r".*\.tempmail\.com.*",
    r".*\.throwawaymail\.com.*",
    r".*\.mailinator\.com.*",
    r".*\.yopmail\.com.*",
    r".*\.getairmail\.com.*",
    r".*\.10minutemail\.com.*",
    r".*\.burnermail\.io.*",
    r".*\.temp-mail\.org.*",
    r".*\.fakeinbox\.com.*",
    r".*\.getnada\.com.*",
    r".*\.maildrop\.cc.*",
    r".*\.harakirimail\.com.*",
    r".*\.mailsac\.com.*",
    r".*\.inbox\.com.*",
    r".*\.pookmail\.com.*",
    r".*\.spambog\.com.*",
    r".*\.trashmail\.com.*",
    r".*\.mailcatch\.com.*",
    r".*\.spamgourmet\.com.*",
    r".*\.bspamfree\.com.*",
    r".*\.spamex\.com.*",
    r".*\.jetable\.com.*",
    r".*\.mailexpire\.com.*",
    r".*\.mailforspam\.com.*",
    r".*\.mailme\.com.*",
    r".*\.mailmetrash\.com.*",
    r".*\.mailshell\.com.*",
    r".*\.mailtothis\.com.*",
    r".*\.mytrashmail\.com.*",
    r".*\.no-spam\.com.*",
    r".*\.nospam\.com.*",
    r".*\.nospam4\.us.*",
    r".*\.nospamfor\.us.*",
    r".*\.nowmymail\.com.*",
    r".*\.objectmail\.com.*",
    r".*\.proxymail\.com.*",
    r".*\.punkass\.com.*",
    r".*\.putthisinyourspamdatabase\.com.*",
    r".*\.quickinbox\.com.*",
    r".*\.recode\.com.*",
    r".*\.recyclemail\.com.*",
    r".*\.rejectmail\.com.*",
    r".*\.rhyta\.com.*",
    r".*\.safetymail\.com.*",
    r".*\.sendspamhere\.com.*",
    r".*\.shiftmail\.com.*",
    r".*\.skeefmail\.com.*",
    r".*\.slopsbox\.com.*",
    r".*\.smellfear\.com.*",
    r".*\.snakemail\.com.*",
    r".*\.sneakemail\.com.*",
    r".*\.sofort-mail\.com.*",
    r".*\.sogetthis\.com.*",
    r".*\.spam\.com.*",
    r".*\.spam4\.me.*",
    r".*\.spamavert\.com.*",
    r".*\.spambob\.com.*",
    r".*\.spambob\.net.*",
    r".*\.spambob\.org.*",
    r".*\.spambog\.com.*",
    r".*\.spambog\.de.*",
    r".*\.spambog\.ru.*",
    r".*\.spambox\.info.*",
    r".*\.spambox\.org.*",
    r".*\.spambox\.us.*",
    r".*\.spamcannon\.com.*",
    r".*\.spamcannon\.net.*",
    r".*\.spamcero\.com.*",
    r".*\.spamcon\.org.*",
    r".*\.spamcorptastic\.com.*",
    r".*\.spamcowboy\.com.*",
    r".*\.spamcowboy\.net.*",
    r".*\.spamcowboy\.org.*",
    r".*\.spamday\.com.*",
    r".*\.spamdecoy\.net.*",
    r".*\.spamex\.com.*",
    r".*\.spamfree\.com.*",
    r".*\.spamfree24\.com.*",
    r".*\.spamfree24\.de.*",
    r".*\.spamfree24\.eu.*",
    r".*\.spamfree24\.info.*",
    r".*\.spamfree24\.net.*",
    r".*\.spamfree24\.org.*",
    r".*\.spamgoes\.in.*",
    r".*\.spamgourmet\.com.*",
    r".*\.spamgourmet\.net.*",
    r".*\.spamgourmet\.org.*",
    r".*\.spamherelots\.com.*",
    r".*\.spamhereplease\.com.*",
    r".*\.spamhole\.com.*",
    r".*\.spamify\.com.*",
    r".*\.spaminator\.de.*",
    r".*\.spamkill\.info.*",
    r".*\.spaml\.com.*",
    r".*\.spaml\.de.*",
    r".*\.spammotel\.com.*",
    r".*\.spamobox\.com.*",
    r".*\.spamoff\.de.*",
    r".*\.spamslicer\.com.*",
    r".*\.spamspot\.com.*",
    r".*\.spamthis\.co\.uk.*",
    r".*\.spamthis\.please\.com.*",
    r".*\.spamtrail\.com.*",
    r".*\.spamtroll\.net.*",
    r".*\.speed\.1s\.fr.*",
    r".*\.supergreatmail\.com.*",
    r".*\.supermailer\.jp.*",
    r".*\.suremail\.info.*",
    r".*\.teewars\.org.*",
    r".*\.teleworm\.com.*",
    r".*\.tempalias\.com.*",
    r".*\.tempe-mail\.com.*",
    r".*\.tempemail\.biz.*",
    r".*\.tempemail\.com.*",
    r".*\.tempemail\.net.*",
    r".*\.tempinbox\.co\.uk.*",
    r".*\.tempinbox\.com.*",
    r".*\.tempmail\.it.*",
    r".*\.tempmail2\.com.*",
    r".*\.tempomail\.fr.*",
    r".*\.temporarily\.de.*",
    r".*\.temporarioemail\.com\.br.*",
    r".*\.temporaryemail\.net.*",
    r".*\.temporaryforwarding\.com.*",
    r".*\.temporaryinbox\.com.*",
    r".*\.thanksnospam\.info.*",
    r".*\.thankyou2010\.com.*",
    r".*\.thisisnotmyrealemail\.com.*",
    r".*\.throwawayemailaddress\.com.*",
    r".*\.tilien\.com.*",
    r".*\.tmailinator\.com.*",
    r".*\.tradermail\.info.*",
    r".*\.trash-amil\.com.*",
    r".*\.trash-mail\.at.*",
    r".*\.trash-mail\.com.*",
    r".*\.trash-mail\.de.*",
    r".*\.trash2009\.com.*",
    r".*\.trashdevil\.com.*",
    r".*\.trashdevil\.de.*",
    r".*\.trashmail\.at.*",
    r".*\.trashmail\.com.*",
    r".*\.trashmail\.de.*",
    r".*\.trashmail\.me.*",
    r".*\.trashmail\.net.*",
    r".*\.trashmail\.org.*",
    r".*\.trashmail\.ws.*",
    r".*\.trashmailer\.com.*",
    r".*\.trashymail\.com.*",
    r".*\.trashymail\.net.*",
    r".*\.trillianpro\.com.*",
    r".*\.turual\.com.*",
    r".*\.twinmail\.de.*",
    r".*\.tyldd\.com.*",
    r".*\.uggsrock\.com.*",
    r".*\.upliftnow\.com.*",
    r".*\.uplipht\.com.*",
    r".*\.venompen\.com.*",
    r".*\.veryrealemail\.com.*",
    r".*\.viditag\.com.*",
    r".*\.viewcastmedia\.com.*",
    r".*\.viewcastmedia\.net.*",
    r".*\.viewcastmedia\.org.*",
    r".*\.webm4il\.info.*",
    r".*\.wegwerfadresse\.de.*",
    r".*\.wegwerfemail\.de.*",
    r".*\.wegwerfmail\.de.*",
    r".*\.wegwerfmail\.net.*",
    r".*\.wegwerfmail\.org.*",
    r".*\.wetrainbayarea\.com.*",
    r".*\.wetrainbayarea\.org.*",
    r".*\.wh4f\.org.*",
    r".*\.whyspam\.me.*",
    r".*\.willselfdestruct\.com.*",
    r".*\.winemaven\.info.*",
    r".*\.wronghead\.com.*",
    r".*\.wuzup\.net.*",
    r".*\.wuzupmail\.net.*",
    r".*\.www\.e4ward\.com.*",
    r".*\.www\.mailinator\.com.*",
    r".*\.wwwnew\.eu.*",
    r".*\.xagloo\.com.*",
    r".*\.xemaps\.com.*",
    r".*\.xents\.com.*",
    r".*\.xmaily\.com.*",
    r".*\.xoxy\.net.*",
    r".*\.yep\.it.*",
    r".*\.yogamaven\.com.*",
    r".*\.yopmail\.com.*",
    r".*\.yopmail\.fr.*",
    r".*\.yopmail\.net.*",
    r".*\.ypmail\.webarnak\.fr\.eu\.org.*",
    r".*\.yuurok\.com.*",
    r".*\.z1p\.biz.*",
    r".*\.za\.com.*",
    r".*\.zehnminuten\.de.*",
    r".*\.zehnminutenmail\.de.*",
    r".*\.zippymail\.info.*",
    r".*\.zoaxe\.com.*",
    r".*\.zoemail\.com.*",
    r".*\.zoemail\.org.*",
    r".*\.zomg\.info.*",
]

# Compile patterns for performance
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in AD_BLOCK_PATTERNS]

# MIME type to extension mapping
MIME_TYPE_MAP = {
    'text/html': '.html',
    'text/css': '.css',
    'text/javascript': '.js',
    'application/javascript': '.js',
    'application/json': '.json',
    'application/pdf': '.pdf',
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/svg+xml': '.svg',
    'video/mp4': '.mp4',
    'video/webm': '.webm',
    'video/ogg': '.ogv',
    'audio/mpeg': '.mp3',
    'audio/wav': '.wav',
    'audio/ogg': '.ogg',
    'audio/webm': '.weba',
    'application/zip': '.zip',
    'application/x-rar-compressed': '.rar',
    'application/x-7z-compressed': '.7z',
    'application/x-tar': '.tar',
    'application/gzip': '.gz',
    'application/x-bzip2': '.bz2',
    'application/x-xz': '.xz',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'application/octet-stream': '.bin',
}


class DownloadThread(QThread):
    """Thread for handling downloads with proper redirect support"""
    progress_updated = pyqtSignal(int, int, int)  # download_id, received, total
    speed_updated = pyqtSignal(int, float)  # download_id, speed_kb/s
    status_updated = pyqtSignal(int, str)  # download_id, status
    finished_signal = pyqtSignal(int, bool, str)  # download_id, success, message
    
    def __init__(self, download_id, url, file_path, parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.url = url
        self.file_path = file_path
        self.is_cancelled = False
        self.manager = QNetworkAccessManager()
        
    def cancel(self):
        self.is_cancelled = True
        
    def run(self):
        try:
            self.status_updated.emit(self.download_id, "Connecting...")
            
            request = QNetworkRequest(QUrl(self.url))
            request.setRawHeader(b'User-Agent', b'HixsBrowser/2.1')
            
            reply = self.manager.get(request)
            
            # Wait for headers
            while not reply.isFinished() and reply.isRunning():
                if self.is_cancelled:
                    reply.abort()
                    self.finished_signal.emit(self.download_id, False, "Cancelled")
                    return
                self.msleep(10)
            
            if reply.error() != QNetworkReply.NoError:
                self.finished_signal.emit(self.download_id, False, f"Error: {reply.errorString()}")
                return
            
            # Check for redirects
            redirect_url = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
            if redirect_url:
                reply.deleteLater()
                self.url = redirect_url.toString()
                self.run()  # Recursive call for redirect
                return
            
            total_size = reply.header(QNetworkRequest.ContentLengthHeader)
            if not total_size:
                total_size = 0
            else:
                total_size = int(total_size)
            
            # Determine file extension from content type if not present
            content_type = reply.header(QNetworkRequest.ContentTypeHeader)
            if content_type and '.' not in os.path.basename(self.file_path):
                ext = MIME_TYPE_MAP.get(str(content_type), '.bin')
                self.file_path += ext
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            file = QFile(self.file_path)
            if not file.open(QIODevice.WriteOnly):
                self.finished_signal.emit(self.download_id, False, "Cannot open file for writing")
                return
            
            received = 0
            last_received = 0
            last_time = time.time()
            
            while not reply.isFinished():
                if self.is_cancelled:
                    reply.abort()
                    file.close()
                    os.remove(self.file_path)
                    self.finished_signal.emit(self.download_id, False, "Cancelled")
                    return
                
                chunk = reply.read(8192)
                if chunk:
                    file.write(chunk)
                    received += len(chunk)
                    
                    current_time = time.time()
                    time_diff = current_time - last_time
                    
                    if time_diff >= 0.5:  # Update every 0.5 seconds
                        self.progress_updated.emit(self.download_id, received, total_size)
                        
                        bytes_diff = received - last_received
                        speed = bytes_diff / 1024 / time_diff  # KB/s
                        self.speed_updated.emit(self.download_id, speed)
                        
                        last_received = received
                        last_time = current_time
                
                self.msleep(1)
            
            file.close()
            reply.deleteLater()
            
            if reply.error() == QNetworkReply.NoError:
                self.progress_updated.emit(self.download_id, received, total_size)
                self.finished_signal.emit(self.download_id, True, "Complete")
            else:
                self.finished_signal.emit(self.download_id, False, f"Error: {reply.errorString()}")
                
        except Exception as e:
            self.finished_signal.emit(self.download_id, False, f"Exception: {str(e)}")


class DownloadItemWidget(QWidget):
    """Widget to display a single download item"""
    cancelled = pyqtSignal(int)
    
    def __init__(self, download_id, filename, url, parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.filename = filename
        self.url = url
        self.file_path = None
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Top row: filename and buttons
        top_layout = QHBoxLayout()
        
        self.filename_label = QLabel(filename)
        self.filename_label.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        self.filename_label.setWordWrap(True)
        top_layout.addWidget(self.filename_label, stretch=1)
        
        # Open button (hidden initially)
        self.open_btn = QPushButton("Open")
        self.open_btn.setMaximumWidth(60)
        self.open_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.open_btn.clicked.connect(self.open_file)
        self.open_btn.setVisible(False)
        top_layout.addWidget(self.open_btn)
        
        # Folder button (hidden initially)
        self.folder_btn = QPushButton("Folder")
        self.folder_btn.setMaximumWidth(60)
        self.folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.folder_btn.clicked.connect(self.open_folder)
        self.folder_btn.setVisible(False)
        top_layout.addWidget(self.folder_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMaximumWidth(70)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.cancel_btn.clicked.connect(lambda: self.cancelled.emit(self.download_id))
        top_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(top_layout)
        
        # URL label
        self.url_label = QLabel(f"URL: {url[:60]}...")
        self.url_label.setStyleSheet("color: #666; font-size: 10px;")
        self.url_label.setWordWrap(True)
        layout.addWidget(self.url_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4285f4;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Bottom row: status and speed
        bottom_layout = QHBoxLayout()
        
        self.status_label = QLabel("Starting...")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        bottom_layout.addWidget(self.status_label)
        
        bottom_layout.addStretch()
        
        self.speed_label = QLabel("0 KB/s")
        self.speed_label.setStyleSheet("color: #666; font-size: 11px;")
        bottom_layout.addWidget(self.speed_label)
        
        self.size_label = QLabel("")
        self.size_label.setStyleSheet("color: #666; font-size: 11px;")
        bottom_layout.addWidget(self.size_label)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            DownloadItemWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)
        
    def update_progress(self, received, total):
        """Update download progress"""
        if total > 0:
            percent = int((received / total) * 100)
            self.progress_bar.setValue(percent)
            
            received_mb = received / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.size_label.setText(f"{received_mb:.1f}/{total_mb:.1f} MB")
        else:
            self.progress_bar.setValue(0)
            received_mb = received / (1024 * 1024)
            self.size_label.setText(f"{received_mb:.1f} MB")
    
    def update_speed(self, speed_kb):
        """Update download speed"""
        if speed_kb > 1024:
            self.speed_label.setText(f"{speed_kb/1024:.1f} MB/s")
        else:
            self.speed_label.setText(f"{speed_kb:.1f} KB/s")
    
    def set_status(self, status):
        """Update status text"""
        self.status_label.setText(status)
    
    def set_complete(self, file_path):
        """Mark download as complete"""
        self.file_path = file_path
        self.progress_bar.setValue(100)
        self.status_label.setText("Complete")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11px;")
        self.speed_label.setText("")
        self.cancel_btn.setVisible(False)
        self.open_btn.setVisible(True)
        self.folder_btn.setVisible(True)
        
    def set_error(self, error_msg):
        """Mark download as error"""
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #f44336; font-size: 11px;")
        self.speed_label.setText("")
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk { background-color: #f44336; }
        """)
        self.cancel_btn.setText("Close")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
        """)
    
    def open_file(self):
        """Open the downloaded file"""
        if self.file_path and os.path.exists(self.file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.file_path))
    
    def open_folder(self):
        """Open the folder containing the downloaded file"""
        if self.file_path:
            folder = os.path.dirname(self.file_path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


class DownloadManagerDialog(QDialog):
    """Download manager dialog with real-time updates"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setMinimumSize(700, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("📥 Downloads")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Clear button
        clear_btn = QPushButton("Clear Completed")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        clear_btn.clicked.connect(self.clear_completed)
        title_layout.addWidget(clear_btn)
        
        layout.addLayout(title_layout)
        
        # Downloads list
        self.downloads_list = QListWidget()
        self.downloads_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.downloads_list.setSpacing(8)
        self.downloads_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f5f5f5;
            }
            QListWidget::item {
                background-color: transparent;
            }
        """)
        layout.addWidget(self.downloads_list)
        
        self.setLayout(layout)
        
        self.download_widgets = {}  # download_id -> (item, widget, thread)
        
    def add_download(self, download_id, filename, url):
        """Add a new download item"""
        item = QListWidgetItem()
        widget = DownloadItemWidget(download_id, filename, url)
        widget.cancelled.connect(self.cancel_download)
        
        item.setSizeHint(widget.sizeHint() + QSize(0, 20))
        
        self.downloads_list.addItem(item)
        self.downloads_list.setItemWidget(item, widget)
        self.download_widgets[download_id] = [item, widget, None]  # thread added later
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.downloads_list.scrollToBottom())
        
    def set_thread(self, download_id, thread):
        """Set the download thread for an item"""
        if download_id in self.download_widgets:
            self.download_widgets[download_id][2] = thread
            
    def update_progress(self, download_id, received, total):
        """Update download progress"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            widget.update_progress(received, total)
    
    def update_speed(self, download_id, speed):
        """Update download speed"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            widget.update_speed(speed)
    
    def set_status(self, download_id, status):
        """Update download status"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            widget.set_status(status)
    
    def set_complete(self, download_id, file_path):
        """Mark download as complete"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            widget.set_complete(file_path)
            item.setSizeHint(widget.sizeHint() + QSize(0, 20))
    
    def set_error(self, download_id, error_msg):
        """Mark download as error"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            widget.set_error(error_msg)
            item.setSizeHint(widget.sizeHint() + QSize(0, 20))
    
    def cancel_download(self, download_id):
        """Cancel a download"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            if thread and thread.isRunning():
                thread.cancel()
                thread.wait(1000)
            self.remove_download(download_id)
    
    def remove_download(self, download_id):
        """Remove a download from the list"""
        if download_id in self.download_widgets:
            item, widget, thread = self.download_widgets[download_id]
            row = self.downloads_list.row(item)
            self.downloads_list.takeItem(row)
            del self.download_widgets[download_id]
    
    def clear_completed(self):
        """Clear completed downloads"""
        items_to_remove = []
        for download_id, (item, widget, thread) in list(self.download_widgets.items()):
            if "Complete" in widget.status_label.text() or "Error" in widget.status_label.text():
                items_to_remove.append(download_id)
        
        for download_id in items_to_remove:
            self.remove_download(download_id)


class DownloadManager(QObject):
    """Manages file downloads with full media support"""
    def __init__(self, browser_window):
        super().__init__()
        self.browser_window = browser_window
        self.active_downloads = {}
        self.download_counter = 0
        self.download_dialog = DownloadManagerDialog(browser_window)
        self.downloads_path = self.get_default_download_path()
        
    def get_default_download_path(self):
        """Get the default downloads folder"""
        downloads_path = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)
        if downloads_path:
            path = downloads_path[0]
        else:
            path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    def handle_download_request(self, download_item):
        """Handle download request from web engine"""
        try:
            self.download_counter += 1
            download_id = self.download_counter
            
            # Get URL and suggested filename
            url = download_item.url().toString()
            suggested_name = download_item.downloadFileName()
            
            if not suggested_name:
                suggested_name = self.extract_filename_from_url(url)
            
            # Clean filename
            suggested_name = self.sanitize_filename(suggested_name)
            
            # Determine file path
            file_path = os.path.join(self.downloads_path, suggested_name)
            
            # Handle duplicates
            counter = 1
            base_name, ext = os.path.splitext(file_path)
            while os.path.exists(file_path):
                file_path = f"{base_name} ({counter}){ext}"
                counter += 1
            
            # Add to download dialog
            self.download_dialog.add_download(download_id, os.path.basename(file_path), url)
            self.download_dialog.show()
            self.download_dialog.raise_()
            self.download_dialog.activateWindow()
            
            # Create and start download thread
            thread = DownloadThread(download_id, url, file_path)
            thread.progress_updated.connect(self.on_progress)
            thread.speed_updated.connect(self.on_speed)
            thread.status_updated.connect(self.on_status)
            thread.finished_signal.connect(self.on_finished)
            
            self.download_dialog.set_thread(download_id, thread)
            self.active_downloads[download_id] = (thread, file_path)
            
            thread.start()
            
            # Update status
            self.browser_window.status_label.setText(f"Downloading: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Download error: {e}")
            QMessageBox.critical(self.browser_window, "Download Error", str(e))
    
    def extract_filename_from_url(self, url):
        """Extract filename from URL"""
        try:
            parsed = urlparse(url)
            path = unquote(parsed.path)
            filename = os.path.basename(path)
            if filename:
                return filename
        except:
            pass
        return "download"
    
    def sanitize_filename(self, filename):
        """Sanitize filename for filesystem"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200] + ext
        return filename or "download"
    
    def on_progress(self, download_id, received, total):
        """Handle download progress"""
        try:
            self.download_dialog.update_progress(download_id, received, total)
        except Exception as e:
            print(f"Progress error: {e}")
    
    def on_speed(self, download_id, speed):
        """Handle speed update"""
        try:
            self.download_dialog.update_speed(download_id, speed)
        except Exception as e:
            print(f"Speed error: {e}")
    
    def on_status(self, download_id, status):
        """Handle status update"""
        try:
            self.download_dialog.set_status(download_id, status)
        except Exception as e:
            print(f"Status error: {e}")
    
    def on_finished(self, download_id, success, message):
        """Handle download completion"""
        try:
            if download_id in self.active_downloads:
                thread, file_path = self.active_downloads[download_id]
                
                if success:
                    self.download_dialog.set_complete(download_id, file_path)
                    self.browser_window.status_label.setText(f"Download complete: {os.path.basename(file_path)}")
                    
                    # Optional: Show notification
                    if self.browser_window.settings.value("show_download_notifications", True, type=bool):
                        self.browser_window.tray_icon.showMessage(
                            "Download Complete",
                            f"{os.path.basename(file_path)} has been downloaded.",
                            QSystemTrayIcon.Information,
                            3000
                        )
                else:
                    self.download_dialog.set_error(download_id, message)
                    self.browser_window.status_label.setText(f"Download failed: {message}")
                
                del self.active_downloads[download_id]
        except Exception as e:
            print(f"Finish error: {e}")


class CustomTabBar(QTabBar):
    """Custom tab bar with close button on each tab and better styling"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideRight)
        self.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 20px 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::close-button {
                image: none;
                subcontrol-position: right;
            }
        """)
        
    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        if index >= 0:
            size.setWidth(max(size.width(), 180))
        return size


class TabGroup:
    """Represents a group of tabs"""
    def __init__(self, name, color="#4285f4"):
        self.name = name
        self.color = color
        self.tab_ids = []  # Store unique IDs instead of indices
    
    def add_tab(self, tab_id):
        if tab_id not in self.tab_ids:
            self.tab_ids.append(tab_id)
    
    def remove_tab(self, tab_id):
        if tab_id in self.tab_ids:
            self.tab_ids.remove(tab_id)


class BrowserTab(QWebEngineView):
    """Custom browser tab with enhanced features"""
    def __init__(self, tab_id, parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.dark_mode_enabled = False
        self.find_text = ""
        self.find_flags = QWebEnginePage.FindFlags()
        
        # Enable all modern web features
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.PrintElementBackgrounds, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanPaste, True)
        
        # Set up page
        self.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 HixsBrowser/2.1"
        )
        
        # Set up permission handling
        self.page().featurePermissionRequested.connect(self.handle_permission_request)
        
        # Enable developer tools
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        
    def handle_permission_request(self, url, feature):
        """Handle permission requests"""
        # Auto-grant common permissions for better UX
        if feature in [
            QWebEnginePage.MediaAudioCapture,
            QWebEnginePage.MediaVideoCapture,
            QWebEnginePage.MediaAudioVideoCapture,
            QWebEnginePage.DesktopVideoCapture,
            QWebEnginePage.DesktopAudioVideoCapture,
            QWebEnginePage.Notifications,
            QWebEnginePage.Geolocation
        ]:
            self.page().setFeaturePermission(
                url, feature, QWebEnginePage.PermissionGrantedByUser
            )
        else:
            self.page().setFeaturePermission(
                url, feature, QWebEnginePage.PermissionDeniedByUser
            )
    
    def set_dark_mode(self, enabled):
        """Inject or remove dark mode CSS"""
        self.dark_mode_enabled = enabled
        try:
            if enabled:
                js_code = """
                (function() {
                    if (document.getElementById('hixs-dark-mode')) return;
                    var style = document.createElement('style');
                    style.id = 'hixs-dark-mode';
                    style.innerHTML = `
                        html {
                            filter: invert(1) hue-rotate(180deg) !important;
                            background-color: #111 !important;
                        }
                        img:not([src*=".svg"]), 
                        video, 
                        canvas, 
                        [style*="background-image"] {
                            filter: invert(1) hue-rotate(180deg) !important;
                        }
                        iframe {
                            filter: invert(1) hue-rotate(180deg) !important;
                        }
                    `;
                    document.head.appendChild(style);
                })();
                """
                self.page().runJavaScript(js_code)
            else:
                js_code = """
                (function() {
                    var style = document.getElementById('hixs-dark-mode');
                    if (style) style.remove();
                })();
                """
                self.page().runJavaScript(js_code)
        except Exception as e:
            print(f"Dark mode error: {e}")
    
    def find_in_page(self, text, forward=True):
        """Find text in page"""
        if not text:
            self.find_text = ""
            self.page().findText("")
            return
            
        self.find_text = text
        flags = QWebEnginePage.FindFlags()
        if not forward:
            flags |= QWebEnginePage.FindBackward
        if self.find_text == text:
            flags |= QWebEnginePage.FindCaseSensitively
            
        self.page().findText(text, flags)
    
    def contextMenuEvent(self, event):
        """Custom context menu with enhanced options"""
        menu = QMenu(self)
        
        # Navigation
        back_action = menu.addAction("← Back")
        back_action.triggered.connect(self.back)
        back_action.setEnabled(self.history().canGoBack())
        
        forward_action = menu.addAction("→ Forward")
        forward_action.triggered.connect(self.forward)
        forward_action.setEnabled(self.history().canGoForward())
        
        reload_action = menu.addAction("↻ Reload")
        reload_action.triggered.connect(self.reload)
        
        menu.addSeparator()
        
        # Edit actions
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.triggerPageAction(QWebEnginePage.Copy))
        
        paste_action = menu.addAction("Paste")
        paste_action.triggered.connect(self.triggerPageAction(QWebEnginePage.Paste))
        
        select_all_action = menu.addAction("Select All")
        select_all_action.triggered.connect(self.selectAll)
        
        menu.addSeparator()
        
        # View source
        view_source_action = menu.addAction("View Page Source")
        view_source_action.triggered.connect(self.view_source)
        
        # Inspect element (if available)
        inspect_action = menu.addAction("Inspect Element")
        inspect_action.triggered.connect(self.inspect_element)
        
        menu.addSeparator()
        
        # Save options
        save_page_action = menu.addAction("Save Page As...")
        save_page_action.triggered.connect(self.save_page)
        
        # Selected text search
        selected_text = self.selectedText()
        if selected_text:
            menu.addSeparator()
            search_action = menu.addAction(f"Search: '{selected_text[:30]}...'")
            search_action.triggered.connect(lambda: self.search_selected_text(selected_text))
            
            copy_text_action = menu.addAction("Copy Selected Text")
            copy_text_action.triggered.connect(lambda: QApplication.clipboard().setText(selected_text))
        
        # Image options
        self.create_image_context_menu(menu, event.pos())
        
        # Link options
        self.create_link_context_menu(menu, event.pos())
        
        menu.exec_(event.globalPos())
    
    def create_image_context_menu(self, menu, pos):
        """Add image-specific options to context menu"""
        # This would require JavaScript to get image URL at position
        pass
    
    def create_link_context_menu(self, menu, pos):
        """Add link-specific options to context menu"""
        # This would require JavaScript to get link URL at position
        pass
    
    def view_source(self):
        """View page source"""
        url = self.url().toString()
        if url:
            main_window = self.window()
            if isinstance(main_window, ModernWebBrowser):
                main_window.add_new_tab(f"view-source:{url}", "Page Source")
    
    def inspect_element(self):
        """Open developer tools (if available)"""
        # Trigger F12 or open dev tools
        self.triggerPageAction(QWebEnginePage.InspectElement)
    
    def save_page(self):
        """Save current page"""
        main_window = self.window()
        if isinstance(main_window, ModernWebBrowser):
            main_window.save_page()
    
    def search_selected_text(self, text):
        """Search for selected text"""
        main_window = self.window()
        if isinstance(main_window, ModernWebBrowser):
            main_window.search_selected_text(text)
    
    def createWindow(self, window_type):
        """Handle new window requests"""
        main_window = self.window()
        if isinstance(main_window, ModernWebBrowser):
            return main_window.add_new_tab()
        return None


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts and blocks ads and trackers"""
    def __init__(self, browser_window):
        super().__init__()
        self.browser_window = browser_window
    
    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            for pattern in COMPILED_PATTERNS:
                if pattern.search(url):
                    info.block(True)
                    self.browser_window.increment_tracker_count()
                    return
        except Exception as e:
            print(f"AdBlock error: {e}")


class FindDialog(QDialog):
    """Find in page dialog"""
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.setWindowTitle("Find in Page")
        self.setFixedWidth(400)
        
        layout = QHBoxLayout()
        
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find...")
        self.find_input.textChanged.connect(self.find_text)
        self.find_input.returnPressed.connect(self.find_next)
        layout.addWidget(self.find_input)
        
        prev_btn = QPushButton("↑")
        prev_btn.setFixedWidth(30)
        prev_btn.clicked.connect(self.find_previous)
        layout.addWidget(prev_btn)
        
        next_btn = QPushButton("↓")
        next_btn.setFixedWidth(30)
        next_btn.clicked.connect(self.find_next)
        layout.addWidget(next_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedWidth(30)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def find_text(self, text):
        self.browser.find_in_page(text, True)
        
    def find_next(self):
        self.browser.find_in_page(self.find_input.text(), True)
        
    def find_previous(self):
        self.browser.find_in_page(self.find_input.text(), False)
        
    def closeEvent(self, event):
        self.browser.find_in_page("")  # Clear search
        super().closeEvent(event)


class ModernWebBrowser(QMainWindow):
    """Main browser window with all features"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hixs Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize settings
        self.settings = QSettings("HixsBrowser", "HixsBrowser")
        self.current_search_engine = self.settings.value("search_engine", "Google")
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.ad_block_enabled = self.settings.value("ad_block_enabled", True, type=bool)
        self.force_dark_website = self.settings.value("force_dark_website", False, type=bool)
        self.tracker_count = 0
        self.tab_groups = []
        self.tab_counter = 0
        self.find_dialog = None
        
        # Check privacy policy agreement on first launch
        self.check_privacy_policy()
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Apply theme
        self.apply_theme()
        
        # Create UI
        self.create_central_widget()
        self.create_toolbar()
        self.create_status_bar()
        self.create_shortcuts()
        
        # Initialize download manager
        self.download_manager = DownloadManager(self)
        
        # Set window icon
        self.set_window_icon()
        
        # Add initial tab
        self.add_new_tab()
        
        # Load saved tabs
        QTimer.singleShot(500, self.load_saved_tabs)
    
    def create_tray_icon(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setVisible(True)
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
    
    def create_central_widget(self):
        """Create central widget and layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tab_bar = CustomTabBar()
        self.tabs.setTabBar(self.tab_bar)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tabs)
    
    def create_toolbar(self):
        """Create the browser toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFixedHeight(45)
        self.addToolBar(toolbar)
        
        # Navigation buttons with better styling
        nav_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
            }
        """
        
        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("Back (Alt+←)")
        self.back_btn.setStyleSheet(nav_style)
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.setToolTip("Forward (Alt+→)")
        self.forward_btn.setStyleSheet(nav_style)
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_btn)
        
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setToolTip("Reload (F5)")
        self.reload_btn.setStyleSheet(nav_style)
        self.reload_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(self.reload_btn)
        
        self.stop_btn = QPushButton("✕")
        self.stop_btn.setToolTip("Stop (Esc)")
        self.stop_btn.setStyleSheet(nav_style + "QPushButton { color: #f44336; }")
        self.stop_btn.clicked.connect(self.stop_loading)
        self.stop_btn.setVisible(False)
        toolbar.addWidget(self.stop_btn)
        
        self.home_btn = QPushButton("⌂")
        self.home_btn.setToolTip("Home (Alt+Home)")
        self.home_btn.setStyleSheet(nav_style)
        self.home_btn.clicked.connect(self.go_home)
        toolbar.addWidget(self.home_btn)
        
        toolbar.addSeparator()
        
        # URL bar container
        url_container = QWidget()
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(0)
        
        # Security indicator
        self.security_btn = QPushButton("🔒")
        self.security_btn.setToolTip("Secure Connection")
        self.security_btn.setFixedSize(28, 28)
        self.security_btn.setStyleSheet("border: none; background: transparent;")
        url_layout.addWidget(self.security_btn)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setMinimumWidth(400)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                border-radius: 20px;
                padding: 6px 15px;
                font-size: 14px;
            }
        """)
        url_layout.addWidget(self.url_bar, stretch=1)
        
        toolbar.addWidget(url_container)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
            }
        """
        
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.setStyleSheet(zoom_style)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(45)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        toolbar.addWidget(self.zoom_label)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_btn.setStyleSheet(zoom_style)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_btn)
        
        toolbar.addSeparator()
        
        # Search engine selector
        self.search_engine_btn = QPushButton(f"🔎 {self.current_search_engine}")
        self.search_engine_btn.setToolTip("Select Search Engine")
        self.search_engine_btn.setFixedSize(110, 30)
        self.search_engine_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                border-radius: 4px;
            }
        """)
        self.search_engine_btn.clicked.connect(self.show_search_engine_menu)
        toolbar.addWidget(self.search_engine_btn)
        
        # Privacy indicator
        self.privacy_btn = QPushButton("🛡️")
        self.privacy_btn.setToolTip("Privacy Dashboard")
        self.privacy_btn.setFixedSize(32, 32)
        self.privacy_btn.setStyleSheet("font-size: 14px; border: none;")
        self.privacy_btn.clicked.connect(self.show_privacy_dashboard)
        toolbar.addWidget(self.privacy_btn)
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙" if not self.dark_mode else "☀️")
        self.theme_btn.setToolTip("Toggle Dark/Light Mode")
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.setStyleSheet("font-size: 14px; border: none;")
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_btn)
        
        # Downloads button
        self.downloads_btn = QPushButton("📥")
        self.downloads_btn.setToolTip("Downloads")
        self.downloads_btn.setFixedSize(32, 32)
        self.downloads_btn.setStyleSheet("font-size: 14px; border: none;")
        self.downloads_btn.clicked.connect(self.show_downloads)
        toolbar.addWidget(self.downloads_btn)
        
        toolbar.addSeparator()
        
        # New tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setToolTip("New Tab (Ctrl+T)")
        new_tab_btn.setFixedSize(32, 32)
        new_tab_btn.setStyleSheet(nav_style + "QPushButton { font-size: 20px; }")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        toolbar.addWidget(new_tab_btn)
        
        # About button
        about_btn = QPushButton("?")
        about_btn.setToolTip("About Hixs Browser")
        about_btn.setFixedSize(32, 32)
        about_btn.setStyleSheet(nav_style)
        about_btn.clicked.connect(self.show_about)
        toolbar.addWidget(about_btn)
        
        # Menu button
        menu_btn = QPushButton("⋮")
        menu_btn.setToolTip("Menu")
        menu_btn.setFixedSize(32, 32)
        menu_btn.setStyleSheet(nav_style)
        menu_btn.clicked.connect(self.show_menu)
        toolbar.addWidget(menu_btn)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Zoom slider (hidden by default)
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(25, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMaximumWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        self.zoom_slider.setVisible(False)
        self.status_bar.addPermanentWidget(self.zoom_slider)
        
        # Tracker count label
        self.tracker_label = QLabel("🛡️ 0 blocked")
        self.tracker_label.setToolTip("Trackers blocked this session")
        self.status_bar.addPermanentWidget(self.tracker_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
    
    def create_shortcuts(self):
        """Create keyboard shortcuts"""
        # Navigation
        QShortcut(QKeySequence("Alt+Left"), self, self.go_back)
        QShortcut(QKeySequence("Alt+Right"), self, self.go_forward)
        QShortcut(QKeySequence(Qt.Key_F5), self, self.reload_page)
        QShortcut(QKeySequence("Ctrl+R"), self, self.reload_page)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.stop_loading)
        QShortcut(QKeySequence("Alt+Home"), self, self.go_home)
        
        # Tabs
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_new_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self.previous_tab)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.switch_to_tab(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.switch_to_tab(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.switch_to_tab(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.switch_to_tab(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.switch_to_tab(4))
        QShortcut(QKeySequence("Ctrl+6"), self, lambda: self.switch_to_tab(5))
        QShortcut(QKeySequence("Ctrl+7"), self, lambda: self.switch_to_tab(6))
        QShortcut(QKeySequence("Ctrl+8"), self, lambda: self.switch_to_tab(7))
        QShortcut(QKeySequence("Ctrl+9"), self, lambda: self.switch_to_tab(self.tabs.count() - 1))
        
        # File operations
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_page)
        QShortcut(QKeySequence("Ctrl+P"), self, self.print_page)
        QShortcut(QKeySequence("Ctrl+U"), self, self.view_page_source)
        
        # Search
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_in_page)
        QShortcut(QKeySequence("Ctrl+G"), self, self.find_next)
        QShortcut(QKeySequence("Ctrl+Shift+G"), self, self.find_previous)
        
        # Zoom
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.reset_zoom)
        
        # Fullscreen
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_full_screen)
        
        # Developer tools
        QShortcut(QKeySequence("F12"), self, self.toggle_dev_tools)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self.toggle_dev_tools)
        
        # Downloads
        QShortcut(QKeySequence("Ctrl+J"), self, self.show_downloads)
        
        # Focus URL bar
        QShortcut(QKeySequence("Ctrl+L"), self, self.focus_url_bar)
        QShortcut(QKeySequence("Alt+D"), self, self.focus_url_bar)
    
    def set_window_icon(self):
        """Set the window icon"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(pixmap)
                    self.setWindowIcon(icon)
                    self.tray_icon.setIcon(icon)
                    return
            
            # Fallback icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#4285f4"))
            painter.drawEllipse(4, 4, 24, 24)
            painter.setBrush(Qt.white)
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "H")
            painter.end()
            icon = QIcon(pixmap)
            self.setWindowIcon(icon)
            self.tray_icon.setIcon(icon)
        except Exception as e:
            print(f"Icon error: {e}")
    
    def add_new_tab(self, url=None, title="New Tab", background=False):
        """Add a new tab with unique ID"""
        # Create browser tab first
        self.tab_counter += 1
        tab_id = self.tab_counter
        
        browser = BrowserTab(tab_id, self)
        
        if url is None:
            url = self.get_homepage()
        
        # Handle hixs://home URL - load custom homepage
        if url == "hixs://home":
            self.load_homepage(browser.page())
        else:
            browser.setUrl(QUrl(url))
        
        # Set up ad blocking
        if self.ad_block_enabled:
            try:
                interceptor = AdBlockInterceptor(self)
                browser.page().profile().setUrlRequestInterceptor(interceptor)
            except Exception as e:
                print(f"AdBlock setup error: {e}")
        
        # Set up download handling
        browser.page().profile().downloadRequested.connect(self.handle_download)
        
        # Connect signals
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_urlbar(qurl, b))
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(lambda success, b=browser: self.on_load_finished(success, b))
        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(title, b))
        browser.iconChanged.connect(lambda icon, b=browser: self.update_tab_icon(icon, b))
        
        # Add tab
        index = self.tabs.addTab(browser, title)
        browser.tab_index = index
        
        if not background:
            self.tabs.setCurrentIndex(index)
        
        # Apply dark mode if enabled
        if self.force_dark_website:
            QTimer.singleShot(1000, lambda: browser.set_dark_mode(True))
        
        return browser
    
    def create_new_tab(self):
        """Create new tab for popups"""
        return self.add_new_tab(background=True)
    
    def close_tab(self, index):
        """Close a tab"""
        if self.tabs.count() > 1:
            browser = self.tabs.widget(index)
            
            # Remove from groups
            for group in self.tab_groups:
                if browser and hasattr(browser, 'tab_id'):
                    group.remove_tab(browser.tab_id)
            
            # Properly cleanup
            self.tabs.removeTab(index)
            if browser:
                browser.deleteLater()
            
            self.save_tabs()
        else:
            self.close()
    
    def close_current_tab(self):
        """Close current tab"""
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)
    
    def next_tab(self):
        """Switch to next tab"""
        current = self.tabs.currentIndex()
        next_index = (current + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(next_index)
    
    def previous_tab(self):
        """Switch to previous tab"""
        current = self.tabs.currentIndex()
        prev_index = (current - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(prev_index)
    
    def switch_to_tab(self, index):
        """Switch to specific tab"""
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        try:
            if index >= 0:
                browser = self.tabs.widget(index)
                if browser:
                    self.update_urlbar(browser.url(), browser)
                    self.update_navigation_buttons()
                    self.update_zoom_label(browser.zoomFactor())
                    
                    # Update security indicator
                    url = browser.url().toString()
                    if url.startswith("https://"):
                        self.security_btn.setText("🔒")
                        self.security_btn.setToolTip("Secure Connection")
                    elif url.startswith("http://"):
                        self.security_btn.setText("⚠️")
                        self.security_btn.setToolTip("Not Secure")
                    else:
                        self.security_btn.setText("")
        except Exception as e:
            print(f"Tab change error: {e}")
    
    def update_navigation_buttons(self):
        """Update back/forward button states"""
        try:
            browser = self.tabs.currentWidget()
            if browser:
                can_back = browser.history().canGoBack()
                can_forward = browser.history().canGoForward()
                
                self.back_btn.setEnabled(can_back)
                self.forward_btn.setEnabled(can_forward)
                
                # Update styles
                opacity = "1.0" if can_back else "0.3"
                self.back_btn.setStyleSheet(f"QPushButton {{ opacity: {opacity}; }}")
                
                opacity = "1.0" if can_forward else "0.3"
                self.forward_btn.setStyleSheet(f"QPushButton {{ opacity: {opacity}; }}")
        except Exception as e:
            print(f"Nav button error: {e}")
    
    def navigate_to_url(self):
        """Navigate to URL"""
        try:
            browser = self.tabs.currentWidget()
            if browser:
                text = self.url_bar.text().strip()
                if text:
                    url = self.process_url_input(text)
                    browser.setUrl(QUrl(url))
        except Exception as e:
            QMessageBox.critical(self, "Navigation Error", str(e))
    
    def process_url_input(self, text):
        """Process URL input with smart detection"""
        text = text.strip()
        
        if not text:
            return self.get_homepage()
        
        # Check for protocol
        if text.startswith(("http://", "https://", "file://", "ftp://", "view-source:")):
            return text
        
        # Check for localhost/IPs
        if re.match(r'^(localhost|127\.0\.0\.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text):
            return f"http://{text}"
        
        # Check if it's a search query
        if " " in text or not "." in text:
            search_url = SEARCH_ENGINES.get(self.current_search_engine, SEARCH_ENGINES["Google"])
            return f"{search_url}{quote(text)}"
        
        # Assume it's a domain
        return f"https://{text}"
    
    def get_homepage(self):
        """Get homepage URL - use Google"""
        return "https://www.google.com"
    
    def load_homepage(self, page):
        """Load custom HTML homepage"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hixs Browser</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
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
                h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
                .tagline { color: #666; font-size: 1.1em; margin-bottom: 30px; }
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
                <h1>Hixs Browser</h1>
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
                    Hixs Browser v2.1 - Privacy First<br>
                    Developed by: geethudinoyt (ruthvik pedapondara)
                </div>
            </div>
            <script>document.getElementById('searchInput').focus();</script>
        </body>
        </html>
        """
        page.setHtml(html)
    
    def update_urlbar(self, qurl, browser=None):
        """Update URL bar"""
        try:
            if browser == self.tabs.currentWidget():
                url = qurl.toString()
                self.url_bar.setText(url)
                self.url_bar.setCursorPosition(0)
        except Exception as e:
            print(f"URL bar error: {e}")
    
    def update_tab_title(self, title, browser):
        """Update tab title"""
        try:
            index = self.tabs.indexOf(browser)
            if index >= 0:
                display_title = title[:25] + "..." if len(title) > 28 else title
                self.tabs.setTabText(index, display_title or "Loading...")
                self.tabs.setTabToolTip(index, title)
        except Exception as e:
            print(f"Tab title error: {e}")
    
    def update_tab_icon(self, icon, browser):
        """Update tab icon"""
        try:
            index = self.tabs.indexOf(browser)
            if index >= 0 and not icon.isNull():
                self.tabs.setTabIcon(index, icon)
        except Exception as e:
            print(f"Tab icon error: {e}")
    
    def on_load_started(self):
        """Handle load start"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Loading...")
        self.reload_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.setWindowTitle("Loading... - Hixs Browser")
    
    def on_load_progress(self, progress):
        """Handle load progress"""
        self.progress_bar.setValue(progress)
    
    def on_load_finished(self, success, browser):
        """Handle load finish"""
        self.progress_bar.setVisible(False)
        self.reload_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        
        if browser == self.tabs.currentWidget():
            title = browser.page().title()
            self.setWindowTitle(f"{title} - Hixs Browser" if title else "Hixs Browser")
            self.status_label.setText("Done" if success else "Failed to load")
            self.update_navigation_buttons()
            self.save_tabs()
            
            if success and self.force_dark_website:
                browser.set_dark_mode(True)
    
    def go_back(self):
        """Go back"""
        browser = self.tabs.currentWidget()
        if browser and browser.history().canGoBack():
            browser.back()
            QTimer.singleShot(100, self.update_navigation_buttons)
    
    def go_forward(self):
        """Go forward"""
        browser = self.tabs.currentWidget()
        if browser and browser.history().canGoForward():
            browser.forward()
            QTimer.singleShot(100, self.update_navigation_buttons)
    
    def reload_page(self):
        """Reload page"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.reload()
    
    def stop_loading(self):
        """Stop loading"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.stop()
            self.progress_bar.setVisible(False)
            self.reload_btn.setVisible(True)
            self.stop_btn.setVisible(False)
            self.status_label.setText("Stopped")
    
    def go_home(self):
        """Go home"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl(self.get_homepage()))
    
    def show_menu(self):
        """Show main menu"""
        menu = QMenu(self)
        
        # File menu
        file_menu = menu.addMenu("📁 File")
        file_menu.addAction("New Tab (Ctrl+T)", lambda: self.add_new_tab())
        file_menu.addAction("Close Tab (Ctrl+W)", self.close_current_tab)
        file_menu.addSeparator()
        file_menu.addAction("Open File... (Ctrl+O)", self.open_file)
        file_menu.addAction("Save Page As... (Ctrl+S)", self.save_page)
        file_menu.addAction("Print... (Ctrl+P)", self.print_page)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menu.addMenu("✏️ Edit")
        edit_menu.addAction("Find in Page (Ctrl+F)", self.find_in_page)
        edit_menu.addAction("Copy URL", self.copy_url)
        
        # View menu
        view_menu = menu.addMenu("👁️ View")
        view_menu.addAction("Zoom In (Ctrl++)", self.zoom_in)
        view_menu.addAction("Zoom Out (Ctrl+-)", self.zoom_out)
        view_menu.addAction("Reset Zoom (Ctrl+0)", self.reset_zoom)
        view_menu.addSeparator()
        view_menu.addAction("Full Screen (F11)", self.toggle_full_screen)
        view_menu.addSeparator()
        
        # Dark mode toggle
        dark_action = view_menu.addAction("Force Dark Mode on Websites")
        dark_action.setCheckable(True)
        dark_action.setChecked(self.force_dark_website)
        dark_action.triggered.connect(self.toggle_force_dark_website)
        
        # History
        history_menu = menu.addMenu("🕐 History")
        history_menu.addAction("Show All History", self.show_history)
        history_menu.addSeparator()
        
        # Add recent history items
        browser = self.tabs.currentWidget()
        if browser:
            history = browser.history()
            for i in range(min(10, history.count())):
                item = history.itemAt(i)
                title = item.title() or item.url().toString()
                action = history_menu.addAction(title[:40])
                action.triggered.connect(lambda checked, url=item.url().toString(): 
                    self.add_new_tab(url))
        
        # Bookmarks
        bookmarks_menu = menu.addMenu("🔖 Bookmarks")
        bookmarks_menu.addAction("Bookmark This Page", self.bookmark_page)
        bookmarks_menu.addAction("Show Bookmarks", self.show_bookmarks)
        
        # Downloads
        downloads_menu = menu.addMenu("📥 Downloads")
        downloads_menu.addAction("Show Downloads (Ctrl+J)", self.show_downloads)
        downloads_menu.addSeparator()
        downloads_menu.addAction("Open Downloads Folder", self.open_downloads_folder)
        
        # Tools
        tools_menu = menu.addMenu("🛠️ Tools")
        tools_menu.addAction("Developer Tools (F12)", self.toggle_dev_tools)
        tools_menu.addAction("View Page Source (Ctrl+U)", self.view_page_source)
        tools_menu.addSeparator()
        tools_menu.addAction("Clear Browsing Data", self.clear_browsing_data)
        
        # Privacy
        privacy_menu = menu.addMenu("🛡️ Privacy")
        privacy_menu.addAction("Privacy Dashboard", self.show_privacy_dashboard)
        
        ad_block_action = privacy_menu.addAction("Ad Blocking")
        ad_block_action.setCheckable(True)
        ad_block_action.setChecked(self.ad_block_enabled)
        ad_block_action.triggered.connect(self.toggle_ad_blocking)
        
        # Search engines
        search_menu = menu.addMenu("🔍 Search Engine")
        for engine in SEARCH_ENGINES.keys():
            action = search_menu.addAction(engine)
            action.setCheckable(True)
            action.setChecked(engine == self.current_search_engine)
            action.triggered.connect(lambda checked, e=engine: self.set_search_engine(e))
        
        # Theme
        theme_menu = menu.addMenu("🎨 Theme")
        light_action = theme_menu.addAction("Light Mode")
        light_action.setCheckable(True)
        light_action.setChecked(not self.dark_mode)
        light_action.triggered.connect(lambda: self.set_theme(False))
        
        dark_action = theme_menu.addAction("Dark Mode")
        dark_action.setCheckable(True)
        dark_action.setChecked(self.dark_mode)
        dark_action.triggered.connect(lambda: self.set_theme(True))
        
        # Help
        help_menu = menu.addMenu("❓ Help")
        help_menu.addAction("About", self.show_about)
        help_menu.addAction("About Developer", self.show_developer)
        
        menu.exec_(QCursor.pos())
    
    def open_file(self):
        """Open local file"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "Web Pages (*.html *.htm);;All Files (*)"
        )
        if path:
            self.add_new_tab(QUrl.fromLocalFile(path).toString())
    
    def save_page(self):
        """Save current page"""
        browser = self.tabs.currentWidget()
        if not browser:
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Page", "",
            "HTML Files (*.html);;All Files (*)"
        )
        if path:
            browser.page().toHtml(lambda html: self.save_html(path, html))
    
    def save_html(self, path, html):
        """Save HTML content to file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.status_label.setText(f"Saved: {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
    
    def print_page(self):
        """Print current page"""
        browser = self.tabs.currentWidget()
        if browser:
            dialog = QPrintDialog(self)
            if dialog.exec_() == QPrintDialog.Accepted:
                browser.page().print(dialog.printer(), lambda success: None)
    
    def view_page_source(self):
        """View page source"""
        browser = self.tabs.currentWidget()
        if browser:
            url = browser.url().toString()
            self.add_new_tab(f"view-source:{url}", "Page Source")
    
    def find_in_page(self):
        """Show find dialog"""
        browser = self.tabs.currentWidget()
        if browser:
            if not self.find_dialog:
                self.find_dialog = FindDialog(browser, self)
            self.find_dialog.show()
            self.find_dialog.raise_()
            self.find_dialog.activateWindow()
    
    def find_next(self):
        """Find next occurrence"""
        browser = self.tabs.currentWidget()
        if browser and self.find_dialog:
            browser.find_in_page(self.find_dialog.find_input.text(), True)
    
    def find_previous(self):
        """Find previous occurrence"""
        browser = self.tabs.currentWidget()
        if browser and self.find_dialog:
            browser.find_in_page(self.find_dialog.find_input.text(), False)
    
    def copy_url(self):
        """Copy current URL"""
        browser = self.tabs.currentWidget()
        if browser:
            url = browser.url().toString()
            QApplication.clipboard().setText(url)
            self.status_label.setText("URL copied to clipboard")
    
    def search_selected_text(self, text):
        """Search selected text"""
        search_url = f"{SEARCH_ENGINES.get(self.current_search_engine, SEARCH_ENGINES['Google'])}{quote(text)}"
        self.add_new_tab(search_url)
    
    def zoom_in(self):
        """Zoom in"""
        browser = self.tabs.currentWidget()
        if browser:
            factor = min(browser.zoomFactor() + 0.1, 5.0)
            browser.setZoomFactor(factor)
            self.update_zoom_label(factor)
    
    def zoom_out(self):
        """Zoom out"""
        browser = self.tabs.currentWidget()
        if browser:
            factor = max(browser.zoomFactor() - 0.1, 0.25)
            browser.setZoomFactor(factor)
            self.update_zoom_label(factor)
    
    def reset_zoom(self):
        """Reset zoom"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.setZoomFactor(1.0)
            self.update_zoom_label(1.0)
    
    def on_zoom_slider_changed(self, value):
        """Handle zoom slider change"""
        browser = self.tabs.currentWidget()
        if browser:
            factor = value / 100.0
            browser.setZoomFactor(factor)
            self.update_zoom_label(factor)
    
    def update_zoom_label(self, factor):
        """Update zoom label"""
        self.zoom_label.setText(f"{int(factor * 100)}%")
    
    def toggle_full_screen(self):
        """Toggle fullscreen"""
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().show()
            self.menuBar().show()
        else:
            self.showFullScreen()
            self.statusBar().hide()
            self.menuBar().hide()
    
    def toggle_dev_tools(self):
        """Toggle developer tools"""
        # Trigger inspect element to open dev tools
        browser = self.tabs.currentWidget()
        if browser:
            browser.triggerPageAction(QWebEnginePage.InspectElement)
    
    def show_history(self):
        """Show history page"""
        self.add_new_tab("chrome://history/", "History")
    
    def bookmark_page(self):
        """Bookmark current page"""
        browser = self.tabs.currentWidget()
        if browser:
            title = browser.page().title()
            url = browser.url().toString()
            
            bookmarks = json.loads(self.settings.value("bookmarks", "[]"))
            bookmarks.append({"title": title, "url": url, "date": datetime.now().isoformat()})
            self.settings.setValue("bookmarks", json.dumps(bookmarks))
            
            self.status_label.setText(f"Bookmarked: {title}")
    
    def show_bookmarks(self):
        """Show bookmarks"""
        # Create bookmarks page
        html = "<html><head><title>Bookmarks</title></head><body>"
        html += "<h1>Bookmarks</h1><ul>"
        
        bookmarks = json.loads(self.settings.value("bookmarks", "[]"))
        for bm in bookmarks:
            html += f'<li><a href="{bm["url"]}">{bm["title"]}</a></li>'
        
        html += "</ul></body></html>"
        
        browser = self.add_new_tab(title="Bookmarks")
        browser.setHtml(html)
    
    def open_downloads_folder(self):
        """Open downloads folder"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.download_manager.downloads_path))
    
    def clear_browsing_data(self):
        """Clear browsing data"""
        reply = QMessageBox.question(
            self, "Clear Browsing Data",
            "Clear all browsing data including history, cookies, and cache?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Clear cache
            QWebEngineProfile.defaultProfile().clearHttpCache()
            self.status_label.setText("Browsing data cleared")
    
    def show_search_engine_menu(self):
        """Show search engine selector"""
        menu = QMenu(self)
        for engine in SEARCH_ENGINES.keys():
            action = menu.addAction(engine)
            action.setCheckable(True)
            action.setChecked(engine == self.current_search_engine)
            action.triggered.connect(lambda checked, e=engine: self.set_search_engine(e))
        menu.exec_(self.search_engine_btn.mapToGlobal(QPoint(0, self.search_engine_btn.height())))
    
    def set_search_engine(self, engine):
        """Set search engine"""
        self.current_search_engine = engine
        self.settings.setValue("search_engine", engine)
        self.search_engine_btn.setText(f"🔎 {engine}")
    
    def toggle_ad_blocking(self):
        """Toggle ad blocking"""
        self.ad_block_enabled = not self.ad_block_enabled
        self.settings.setValue("ad_block_enabled", self.ad_block_enabled)
        QMessageBox.information(
            self, "Ad Blocking",
            f"Ad blocking {'enabled' if self.ad_block_enabled else 'disabled'}.\n"
            "Restart browser to apply to all tabs."
        )
    
    def toggle_force_dark_website(self):
        """Toggle force dark mode"""
        self.force_dark_website = not self.force_dark_website
        self.settings.setValue("force_dark_website", self.force_dark_website)
        
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser:
                browser.set_dark_mode(self.force_dark_website)
    
    def toggle_theme(self):
        """Toggle theme"""
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self.apply_theme()
        self.theme_btn.setText("🌙" if not self.dark_mode else "☀️")
    
    def set_theme(self, dark):
        """Set theme"""
        if self.dark_mode != dark:
            self.toggle_theme()
    
    def apply_theme(self):
        """Apply theme stylesheet"""
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; }
                QToolBar { 
                    background-color: #2d2d2d; 
                    border: none; 
                    padding: 4px;
                    spacing: 4px;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                    color: #ffffff;
                }
                QPushButton:hover { background-color: #4d4d4d; }
                QPushButton:pressed { background-color: #2d2d2d; }
                QPushButton:disabled { color: #666; }
                QLineEdit {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    color: #ffffff;
                }
                QLineEdit:focus { border-color: #4285f4; }
                QTabWidget::pane { border: 1px solid #3d3d3d; background-color: #1e1e1e; }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #cccccc;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    border-bottom: 2px solid #4285f4;
                    color: #ffffff;
                }
                QTabBar::tab:hover:!selected { background-color: #3d3d3d; }
                QStatusBar { background-color: #2d2d2d; color: #cccccc; }
                QLabel { color: #cccccc; }
                QMenu {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                }
                QMenu::item:selected { background-color: #4285f4; }
                QProgressBar { border: none; background-color: transparent; }
                QProgressBar::chunk { background-color: #4285f4; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #f5f5f5; }
                QToolBar { 
                    background-color: #ffffff; 
                    border: none;
                    padding: 4px;
                    spacing: 4px;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #f0f0f0; }
                QPushButton:pressed { background-color: #e8e8e8; }
                QPushButton:disabled { color: #aaa; }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                }
                QLineEdit:focus { border-color: #4285f4; }
                QTabWidget::pane { border: 1px solid #e0e0e0; background-color: #ffffff; }
                QTabBar::tab {
                    background-color: #f8f8f8;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 2px solid #4285f4;
                }
                QTabBar::tab:hover:!selected { background-color: #f0f0f0; }
                QStatusBar { background-color: #ffffff; }
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                }
                QMenu::item:selected { background-color: #f0f0f0; }
                QProgressBar { border: none; background-color: transparent; }
                QProgressBar::chunk { background-color: #4285f4; }
            """)
    
    def show_privacy_dashboard(self):
        """Show privacy dashboard"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Privacy Dashboard")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Stats
        stats = QLabel(
            f"<h2>🛡️ Privacy Protection</h2>"
            f"<p><b>Trackers Blocked:</b> {self.tracker_count}</p>"
            f"<p><b>Ad Blocking:</b> {'Enabled' if self.ad_block_enabled else 'Disabled'}</p>"
            f"<p><b>Search Engine:</b> {self.current_search_engine}</p>"
            f"<p><b>Theme:</b> {'Dark' if self.dark_mode else 'Light'}</p>"
            f"<p><b>Tabs Open:</b> {self.tabs.count()}</p>"
        )
        stats.setWordWrap(True)
        layout.addWidget(stats)
        
        # Clear data button
        clear_btn = QPushButton("Clear All Browsing Data")
        clear_btn.clicked.connect(self.clear_browsing_data)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.accepted.connect(dialog.accept)
        layout.addWidget(btn_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def increment_tracker_count(self):
        """Increment tracker counter"""
        self.tracker_count += 1
        self.tracker_label.setText(f"🛡️ {self.tracker_count} blocked")
    
    def show_downloads(self):
        """Show downloads dialog"""
        self.download_manager.download_dialog.show()
        self.download_manager.download_dialog.raise_()
        self.download_manager.download_dialog.activateWindow()
    
    def handle_download(self, download_item):
        """Handle download request"""
        self.download_manager.handle_download_request(download_item)
    
    def save_tabs(self):
        """Save tabs to settings"""
        try:
            tabs_data = []
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if browser:
                    url = browser.url().toString()
                    if url and not url.startswith("view-source:"):
                        tabs_data.append({
                            "url": url,
                            "title": self.tabs.tabText(i)
                        })
            
            self.settings.setValue("saved_tabs", json.dumps(tabs_data))
        except Exception as e:
            print(f"Save tabs error: {e}")
    
    def load_saved_tabs(self):
        """Load saved tabs"""
        try:
            tabs_json = self.settings.value("saved_tabs", "[]")
            tabs_data = json.loads(tabs_json)
            
            if tabs_data and len(tabs_data) > 0:
                reply = QMessageBox.question(
                    self, "Restore Session",
                    f"Restore {len(tabs_data)} tabs from last session?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Close default tab
                    if self.tabs.count() == 1:
                        browser = self.tabs.widget(0)
                        if browser and browser.url().toString() == self.get_homepage():
                            self.tabs.removeTab(0)
                    
                    for tab in tabs_data:
                        self.add_new_tab(tab["url"], tab["title"])
                        
        except Exception as e:
            print(f"Load tabs error: {e}")
    
    def focus_url_bar(self):
        """Focus URL bar"""
        self.url_bar.selectAll()
        self.url_bar.setFocus()
    
    def check_privacy_policy(self):
        """Check if user has agreed to privacy policy"""
        privacy_agreed = self.settings.value("privacy_agreed", False, type=bool)
        
        if not privacy_agreed:
            # Show privacy policy dialog
            msg = QMessageBox(self)
            msg.setWindowTitle("Privacy Policy")
            msg.setText("<h2>Privacy Policy Agreement</h2>")
            msg.setInformativeText(
                "Welcome to Hixs Browser!\n\n"
                "Before using the browser, please read and agree to our Privacy Policy.\n\n"
                "By clicking 'Agree', you acknowledge that:\n"
                "- We collect minimal data for browser functionality\n"
                "- Your browsing data is stored locally on your device\n"
                "- We block ads and trackers for privacy\n\n"
                "Click 'View Privacy Policy' to read the full policy."
            )
            
            # Add buttons
            view_btn = msg.addButton("View Privacy Policy", QMessageBox.ActionRole)
            agree_btn = msg.addButton("Agree & Continue", QMessageBox.AcceptRole)
            decline_btn = msg.addButton("Decline", QMessageBox.RejectRole)
            
            msg.setDefaultButton(agree_btn)
            msg.exec_()
            
            if msg.clickedButton() == view_btn:
                # Open privacy policy in new tab
                self.add_new_tab("privacy.html", "Privacy Policy")
                # Show again after viewing
                QTimer.singleShot(1000, self.check_privacy_policy)
            elif msg.clickedButton() == decline_btn:
                # User declined - close browser
                QMessageBox.information(self, "Thank You", "You need to agree to the Privacy Policy to use Hixs Browser.")
                self.close()
                return
            else:
                # User agreed - save preference
                self.settings.setValue("privacy_agreed", True)
    
    def show_developer(self):
        """Show developer info - opens dev.html in new tab"""
        self.add_new_tab("dev.html", "About Developer")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Hixs Browser",
            "<h2>Hixs Browser v2.1</h2>"
            "<p>A modern, privacy-focused web browser built with PyQt5.</p>"
            "<h3>Features:</h3>"
            "<ul>"
            "<li>Advanced ad and tracker blocking</li>"
            "<li>Full download manager with media support</li>"
            "<li>Dark mode for all websites</li>"
            "<li>Multiple search engines</li>"
            "<li>Tab management and groups</li>"
            "<li>Privacy dashboard</li>"
            "<li>Developer tools</li>"
            "<li>Bookmarks and history</li>"
            "</ul>"
            "<hr>"
            "<p><b>Developed by:</b> geethudinoyt (ruthvik pedapondara)</p>"
            "<p><b>Built with:</b> Python, PyQt5, QtWebEngine</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close"""
        self.save_tabs()
        # Stop all downloads
        for download_id, (thread, path) in list(self.download_manager.active_downloads.items()):
            thread.cancel()
            thread.wait(1000)
        event.accept()


if __name__ == "__main__":
    # Enable High DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Hixs Browser")
    app.setOrganizationName("Hixs Studios")
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    browser = ModernWebBrowser()
    browser.show()
    
    sys.exit(app.exec_())