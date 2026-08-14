#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SITE_ORIGIN = "https://www.automicvault.com"
PACKAGE_ORIGIN = "https://pkg.so"
LOCALES_PATH = Path("data/www-i18n/locales.json")
STATIC_PATH = Path("data/www-i18n/static/pages.json")
SITE_DIR = Path("www")
SITEMAP_PATH = SITE_DIR / "sitemap.xml"
I18N_SCRIPT = SITE_DIR / "i18n.js"
GOOGLE_ANALYTICS_TAG = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y78QKG1T9Y"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-Y78QKG1T9Y');
  </script>"""


@dataclass(frozen=True)
class Locale:
    code: str
    slug: str
    html_lang: str
    hreflang: str
    display_name: str
    native_name: str
    browser_languages: tuple[str, ...]
    enabled: bool


TOPICS: dict[str, dict[str, dict[str, Any]]] = {
    "download": {
        "en": {"title": "Download Automic Vault", "description": "Download Automic Vault for macOS and protect local AI agent runs.", "kicker": "Download", "h1": "Download Automic Vault for macOS", "lede": "Install the local security layer for CLI secrets, developer tools, and AI agent actions on macOS.", "sections": [["Direct download", "Download the signed .dmg, open Automic Vault, and follow the setup guide to install the av command-line tool."], ["What is included", "The native app manages Authorization Gates, Authorization Policies, Tool Hardening, and local Authorization History."], ["After installation", "Move a Credential out of plaintext storage, choose which Verified Launchers may use it, then review each sensitive request before it runs."]]},
        "ja": {"title": "Automic Vault ダウンロード", "description": "macOS 用 Automic Vault を入手し、ローカルの AI エージェント実行を保護します。", "kicker": "ダウンロード", "h1": "macOS 用 Automic Vault をダウンロード", "lede": "ローカルの Homebrew パッケージ、CLI シークレット、AI エージェント操作を保護する macOS セキュリティレイヤーをインストールします。", "sections": [["直接ダウンロード", ".dmg を取得するか、ターミナル用の install.sh スクリプトでインストールできます。"], ["含まれるもの", "ネイティブアプリ、av コマンドラインツール、シークレットスキャナー、Nucleus パッケージ制御が含まれます。"], ["インストール後", "まずシークレットスキャナーを実行し、平文の認証情報を確認して、対応済みのシークレットを保護されたローカル保存に移します。"]]},
        "de": {"title": "Automic Vault herunterladen", "description": "Lade Automic Vault für macOS herunter und schütze lokale AI-Agent-Läufe.", "kicker": "Download", "h1": "Automic Vault für macOS herunterladen", "lede": "Installiere die lokale Sicherheitschicht für Homebrew-Pakete, CLI-Secrets und AI-Agent-Aktionen auf macOS.", "sections": [["Direkter Download", "Lade die .dmg-Datei herunter oder installiere über das install.sh-Skript im Terminal."], ["Was enthalten ist", "Enthalten sind die native App, das av-Kommandozeilenwerkzeug, Secret-Scanner-Workflows und Nucleus-Paketkontrollen."], ["Nach der Installation", "Starte zuerst den Secret Scanner, prüfe Klartext-Credentials und verschiebe unterstützte Secrets in geschützten lokalen Speicher."]]},
        "fr": {"title": "Télécharger Automic Vault", "description": "Téléchargez Automic Vault pour macOS et protégez les exécutions locales d'agents IA.", "kicker": "Téléchargement", "h1": "Télécharger Automic Vault pour macOS", "lede": "Installez la couche de sécurité locale pour les paquets Homebrew, les secrets CLI et les actions d'agents IA sur macOS.", "sections": [["Téléchargement direct", "Téléchargez le .dmg ou installez depuis le terminal avec le script install.sh."], ["Ce qui est inclus", "Le téléchargement inclut l'application native, l'outil en ligne de commande av, les workflows de scanner de secrets et les contrôles de paquets Nucleus."], ["Après l'installation", "Lancez d'abord le scanner de secrets, vérifiez les identifiants en clair et déplacez les secrets pris en charge vers un stockage local protégé."]]},
        "zh-Hans": {"title": "下载 Automic Vault", "description": "获取 macOS 版 Automic Vault，保护本地 AI 代理运行。", "kicker": "下载", "h1": "下载 macOS 版 Automic Vault", "lede": "安装用于保护 macOS 上 Homebrew 软件包、CLI 密钥和 AI 代理操作的本地安全层。", "sections": [["直接下载", "可以下载 .dmg，也可以在终端中使用 install.sh 脚本安装。"], ["包含内容", "下载内容包括原生应用、av 命令行工具、密钥扫描器工作流和 Nucleus 软件包控制。"], ["安装之后", "先运行密钥扫描器，检查明文凭据，并将支持的密钥移入受保护的本地存储。"]]},
    },
    "privacy": {
        "ja": {
            "title": "Automic Vault プライバシー",
            "description": "Automic Vault の Mac アプリとウェブサイトが送信するデータ、ローカルに残るデータ、利用する解析サービス。",
            "h1": "シークレットはローカルに残り、製品メトリクスは Mac の外へ送信されます",
            "sections": [
                ["製品データ", "シークレットと認証履歴は Mac に残ります。リリース版アプリは、利用状況と Mac の技術情報を PostHog に送信します。"],
                ["アプリの利用状況", "アプリはランダムなインストール識別子を環境設定に保存し、同じインストールから届くイベントを関連付けます。送信するイベントは、メインウィンドウを開いたこと、検出された Detector 数の変化、リクエストを承認したことです。"],
                ["送信しないデータ", "シークレット、シークレット名、コマンド、引数、作業ディレクトリ、Launcher や Target の識別情報、Finding の名前やパス、認証履歴は送信しません。"],
                ["送信先と目的", "アプリは us.i.posthog.com の PostHog Cloud US にデータを送信します。機能の利用状況と互換性を把握するために使い、広告、データ販売、他製品をまたぐ追跡には使いません。"],
                ["ウェブサイト", "ウェブサイトは Google Analytics を使い、ページ表示、ブラウザ、端末、参照元、ネットワークのデータを処理します。Mac アプリに保存されたシークレットをウェブサイトが受け取ることはありません。"],
                ["制御", "現在の Mac アプリにはテレメトリの切り替えがありません。ネットワークフィルターで us.i.posthog.com を遮断すると、アプリのメトリクス送信を止められます。削除依頼は mxcl@me.com までご連絡ください。"],
            ],
        },
        "de": {
            "title": "Automic Vault Datenschutz",
            "description": "Welche Daten die Automic-Vault-App und Website senden, was lokal bleibt und welche Analysedienste Daten erhalten.",
            "h1": "Secrets bleiben lokal, Produktmetriken verlassen den Mac",
            "sections": [
                ["Produktdaten", "Secrets und Authorization History bleiben auf dem Mac. Release-Builds senden Nutzungsereignisse und technische Mac-Daten an PostHog."],
                ["App-Nutzung", "Die App speichert eine zufällige Installationskennung in ihren Einstellungen und verknüpft damit Ereignisse derselben Installation. Sie meldet das Öffnen des Hauptfensters, Änderungen an der Zahl ausgelöster Detectors und die Tatsache, dass ein Request genehmigt wurde."],
                ["Nicht gesendete Daten", "Die App sendet keine Secrets, Secret Names, Befehle, Argumente, Arbeitsverzeichnisse, Launcher- oder Target-Identitäten, Finding-Namen oder -Pfade und keine Authorization History."],
                ["Ziel und Zweck", "Die App sendet Daten an PostHog Cloud US unter us.i.posthog.com. Wir nutzen sie für Funktionsnutzung und Kompatibilität, nicht für Werbung, Datenverkauf oder produktübergreifendes Tracking."],
                ["Website", "Die Website nutzt Google Analytics. Google verarbeitet Seitenaufrufe sowie Browser-, Geräte-, Referrer- und Netzwerkdaten. Die Website erhält keine Secrets aus der Mac-App."],
                ["Kontrolle", "Die aktuelle Mac-App hat keinen Telemetrie-Schalter. Ein Netzwerkfilter für us.i.posthog.com stoppt die Produktmetriken. Löschanfragen können an mxcl@me.com gesendet werden."],
            ],
        },
        "fr": {
            "title": "Confidentialité Automic Vault",
            "description": "Les données envoyées par l’app Mac et le site Automic Vault, celles qui restent locales et les services d’analyse utilisés.",
            "h1": "Les Secrets restent locaux, les métriques produit quittent le Mac",
            "sections": [
                ["Données produit", "Les Secrets et l’historique des autorisations restent sur le Mac. Les versions distribuées envoient des événements d’utilisation et des caractéristiques techniques du Mac à PostHog."],
                ["Utilisation de l’app", "L’app stocke un identifiant d’installation aléatoire dans ses préférences pour relier les événements d’une même installation. Elle signale l’ouverture de la fenêtre principale, les changements du nombre de Detectors déclenchés et le fait qu’une requête a été approuvée."],
                ["Données non envoyées", "L’app n’envoie aucun Secret, nom de Secret, commande, argument, dossier courant, identité de Launcher ou de Target, nom ou chemin de Finding, ni historique d’autorisation."],
                ["Destination et usage", "L’app envoie les données à PostHog Cloud US sur us.i.posthog.com. Nous les utilisons pour mesurer l’usage des fonctions et la compatibilité, sans publicité, vente de données ni suivi entre produits."],
                ["Site web", "Le site utilise Google Analytics. Google traite les pages consultées ainsi que les données du navigateur, de l’appareil, du référent et du réseau. Le site ne reçoit aucun Secret stocké dans l’app Mac."],
                ["Contrôle", "L’app Mac actuelle ne propose pas d’interrupteur de télémétrie. Un filtre réseau bloquant us.i.posthog.com arrête les métriques de l’app. Les demandes de suppression peuvent être envoyées à mxcl@me.com."],
            ],
        },
        "zh-Hans": {
            "title": "Automic Vault 隐私",
            "description": "Automic Vault Mac 应用和网站发送哪些数据、哪些数据留在本地，以及哪些分析服务会接收数据。",
            "h1": "密钥留在本地，产品指标会离开 Mac",
            "sections": [
                ["产品数据", "密钥和授权历史记录留在 Mac 上。发布版本会把使用事件和 Mac 技术信息发送给 PostHog。"],
                ["应用使用情况", "应用会在偏好设置中保存一个随机安装标识符，用它关联同一次安装产生的事件。事件包括打开主窗口、触发的 Detector 数量发生变化，以及用户批准了请求。"],
                ["不会发送的数据", "应用不会发送密钥、密钥名称、命令、参数、工作目录、Launcher 或 Target 身份、Finding 名称或路径，也不会发送授权历史记录。"],
                ["接收方和用途", "应用把数据发送到 us.i.posthog.com 上的 PostHog Cloud US。我们用这些数据了解功能使用情况和兼容性，不用于广告、出售数据或跨产品跟踪。"],
                ["网站", "网站使用 Google Analytics。Google 会处理页面浏览记录，以及浏览器、设备、来源和网络数据。网站不会收到 Mac 应用中存储的密钥。"],
                ["控制方式", "当前 Mac 应用没有遥测开关。通过网络过滤器阻止 us.i.posthog.com 可以停止应用指标发送。数据删除请求可发送至 mxcl@me.com。"],
            ],
        },
    },
    "terms": {
        "ja": {"title": "Automic Vault 利用規約", "description": "Automic Vault の利用条件、オープンソースライセンス、ウェブサイト利用メモ。", "h1": "オープンソースのローカルセキュリティツール", "sections": [["ライセンス", "Automic Vault は Apache License 2.0 の下で提供されます。"], ["利用", "このサイトは製品情報、ドキュメント、パッケージメタデータを提供します。"]]},
        "de": {"title": "Automic Vault Bedingungen", "description": "Nutzungsbedingungen, Open-Source-Lizenz und Website-Hinweise für Automic Vault.", "h1": "Open-Source-Werkzeug für lokale Sicherheit", "sections": [["Lizenz", "Automic Vault wird unter der Apache License 2.0 bereitgestellt."], ["Nutzung", "Diese Website stellt Produktinformationen, Dokumentation und Paketmetadaten bereit."]]},
        "fr": {"title": "Conditions Automic Vault", "description": "Conditions d'utilisation, licence open source et notes du site pour Automic Vault.", "h1": "Outil open source de sécurité locale", "sections": [["Licence", "Automic Vault est fourni sous licence Apache License 2.0."], ["Utilisation", "Ce site fournit des informations produit, de la documentation et des métadonnées de paquets."]]},
        "zh-Hans": {"title": "Automic Vault 条款", "description": "Automic Vault 的使用条款、开源许可证和网站说明。", "h1": "开源本地安全工具", "sections": [["许可证", "Automic Vault 以 Apache License 2.0 提供。"], ["使用", "本网站提供产品信息、文档和软件包元数据。"]]},
    },
}

DOWNLOAD_IMAGE_ALTS: dict[str, tuple[str, str, str]] = {
    "en": (
        "Automic Vault approval prompt showing ChatGPT requesting a GitHub token",
        "Automic Vault access rules for a Supabase secret across Terminal and ChatGPT",
        "Automic Vault secret-use log showing denied and approved GitHub CLI requests",
    ),
    "ja": (
        "ChatGPT が GitHub トークンを要求する Automic Vault の承認画面",
        "Terminal と ChatGPT に対する Supabase シークレットのアクセス規則",
        "拒否および承認された GitHub CLI リクエストの利用履歴",
    ),
    "de": (
        "Automic-Vault-Freigabe für eine GitHub-Token-Anfrage von ChatGPT",
        "Automic-Vault-Zugriffsregeln für ein Supabase-Secret in Terminal und ChatGPT",
        "Automic-Vault-Protokoll mit abgelehnten und genehmigten GitHub-CLI-Anfragen",
    ),
    "fr": (
        "Demande d’approbation Automic Vault pour un jeton GitHub requis par ChatGPT",
        "Règles d’accès Automic Vault pour un secret Supabase dans Terminal et ChatGPT",
        "Journal Automic Vault des requêtes GitHub CLI refusées et approuvées",
    ),
    "zh-Hans": (
        "ChatGPT 请求 GitHub 令牌时显示的 Automic Vault 审批界面",
        "Terminal 与 ChatGPT 使用 Supabase 密钥的 Automic Vault 访问规则",
        "Automic Vault 中被拒绝和批准的 GitHub CLI 请求记录",
    ),
}

UI_COPY: dict[str, dict[str, str]] = {
    "en": {
        "about": "About",
        "brandHomeAria": "Automic Vault home",
        "dismissLanguageSuggestion": "Dismiss language suggestion",
        "docs": "Docs",
        "download": "Download",
        "languageSuggestionAria": "Language suggestion",
        "languageSuggestionText": "Read this page in English",
        "languageVersionsAria": "Language versions",
        "mainNavigationAria": "Main navigation",
        "packages": "Packages",
        "privacy": "Privacy",
        "security": "Security",
        "terms": "Terms",
        "website": "Website",
    },
    "ja": {
        "about": "概要",
        "brandHomeAria": "Automic Vault ホーム",
        "dismissLanguageSuggestion": "言語提案を閉じる",
        "docs": "ドキュメント",
        "download": "ダウンロード",
        "languageSuggestionAria": "言語の提案",
        "languageSuggestionText": "このページを日本語で読む",
        "languageVersionsAria": "言語版",
        "mainNavigationAria": "メインナビゲーション",
        "packages": "パッケージ",
        "privacy": "プライバシー",
        "security": "セキュリティ",
        "terms": "利用規約",
        "website": "ウェブサイト",
    },
    "de": {
        "about": "Über uns",
        "brandHomeAria": "Automic Vault Startseite",
        "dismissLanguageSuggestion": "Sprachvorschlag schließen",
        "docs": "Dokumentation",
        "download": "Herunterladen",
        "languageSuggestionAria": "Sprachvorschlag",
        "languageSuggestionText": "Diese Seite auf Deutsch lesen",
        "languageVersionsAria": "Sprachversionen",
        "mainNavigationAria": "Hauptnavigation",
        "packages": "Pakete",
        "privacy": "Datenschutz",
        "security": "Sicherheit",
        "terms": "Bedingungen",
        "website": "Website",
    },
    "fr": {
        "about": "À propos",
        "brandHomeAria": "Accueil Automic Vault",
        "dismissLanguageSuggestion": "Fermer la suggestion de langue",
        "docs": "Documentation",
        "download": "Télécharger",
        "languageSuggestionAria": "Suggestion de langue",
        "languageSuggestionText": "Lire cette page en français",
        "languageVersionsAria": "Versions linguistiques",
        "mainNavigationAria": "Navigation principale",
        "packages": "Paquets",
        "privacy": "Confidentialité",
        "security": "Sécurité",
        "terms": "Conditions",
        "website": "Site web",
    },
    "zh-Hans": {
        "about": "关于",
        "brandHomeAria": "Automic Vault 首页",
        "dismissLanguageSuggestion": "关闭语言建议",
        "docs": "文档",
        "download": "下载",
        "languageSuggestionAria": "语言建议",
        "languageSuggestionText": "用简体中文阅读本页",
        "languageVersionsAria": "语言版本",
        "mainNavigationAria": "主导航",
        "packages": "软件包",
        "privacy": "隐私",
        "security": "安全",
        "terms": "条款",
        "website": "网站",
    },
}

LLMS_COPY: dict[str, dict[str, str]] = {
    "ja": {
        "summary": "Automic Vault は CLI シークレットを平文ファイルから除き、承認済みの Mac アプリだけがローカル実行境界で使用できるようにします。",
        "pages": "主要ページ",
        "packagesDescription": "開発者向けパッケージ、依存関係、インストール方法、リスク情報、Automic Vault の保護状況を検索できます。",
        "docsDescription": "Automic Vault 2.9.0 の scan、doctor、save、inject、bless、harden などを解説する英語の CLI マニュアルです。",
        "blogDescription": "パッケージ、エディタ拡張、認証情報、ローカル実行のインシデント分析と開発者向けセキュリティガイドです。",
        "sourceDescription": "Apache-2.0 のソースコード、タグ付きリリース、実装履歴、公開 Issue を掲載しています。",
        "securityDescription": "現在のセキュリティ連絡先、優先言語、正規 URL、有効期限を公開しています。",
        "facts": "基本情報",
        "platform": "対応環境: macOS",
        "release": "現在のドキュメント対象リリース: 2.9.0",
        "license": "ライセンス: Apache License 2.0",
        "pricing": "価格: 無料のオープンソースソフトウェア",
        "founder": "創設者: Homebrew 作者の Max Howell",
        "contact": "連絡先",
        "securityReports": "セキュリティ報告",
    },
    "de": {
        "summary": "Automic Vault entfernt Klartext-Secrets aus CLI-Tools und steuert am lokalen Ausführungsrand, welche signierten Mac-Apps sie verwenden dürfen.",
        "pages": "Wichtige Seiten",
        "packagesDescription": "Durchsuchbarer Katalog mit Entwicklerpaketen, Abhängigkeiten, Installationsbefehlen, Risikoinformationen und Automic-Vault-Härtung.",
        "docsDescription": "Englisches, quellgeprüftes CLI-Handbuch für Automic Vault 2.9.0 mit scan, doctor, save, inject, bless und harden.",
        "blogDescription": "Sicherheitsleitfäden und Analysen zu Paket-, Erweiterungs-, Credential- und lokalen Ausführungsvorfällen.",
        "sourceDescription": "Apache-2.0-Quellcode, markierte Releases, Implementierungshistorie und öffentliche Fehlerverfolgung.",
        "securityDescription": "Veröffentlicht den aktuellen Sicherheitskontakt, die bevorzugte Sprache, die kanonische Adresse und das Ablaufdatum.",
        "facts": "Kernfakten",
        "platform": "Plattform: macOS",
        "release": "Aktuell dokumentiertes Release: 2.9.0",
        "license": "Lizenz: Apache License 2.0",
        "pricing": "Preis: kostenlose Open-Source-Software",
        "founder": "Gründer: Max Howell, Schöpfer von Homebrew",
        "contact": "Kontakt",
        "securityReports": "Sicherheitsmeldungen",
    },
    "fr": {
        "summary": "Automic Vault retire les secrets en clair des outils CLI et contrôle quelles apps Mac signées peuvent les utiliser à la limite d’exécution locale.",
        "pages": "Pages principales",
        "packagesDescription": "Catalogue consultable de paquets développeur, dépendances, commandes d’installation, risques et couverture de durcissement Automic Vault.",
        "docsDescription": "Manuel CLI en anglais, vérifié sur les sources d’Automic Vault 2.9.0, couvrant scan, doctor, save, inject, bless et harden.",
        "blogDescription": "Guides et analyses d’incidents liés aux paquets, extensions, identifiants et exécutions locales.",
        "sourceDescription": "Code source Apache-2.0, versions étiquetées, historique d’implémentation et suivi public des problèmes.",
        "securityDescription": "Publie le contact de sécurité actuel, la langue préférée, l’adresse canonique et la date d’expiration.",
        "facts": "Faits essentiels",
        "platform": "Plateforme : macOS",
        "release": "Version actuellement documentée : 2.9.0",
        "license": "Licence : Apache License 2.0",
        "pricing": "Prix : logiciel open source gratuit",
        "founder": "Fondateur : Max Howell, créateur de Homebrew",
        "contact": "Contact",
        "securityReports": "Signalements de sécurité",
    },
    "zh-Hans": {
        "summary": "Automic Vault 从 CLI 工具中移除明文密钥，并在本地执行边界控制哪些已签名 Mac 应用可以使用它们。",
        "pages": "主要页面",
        "packagesDescription": "可搜索开发者软件包、依赖项、安装命令、风险信息和 Automic Vault 加固覆盖情况。",
        "docsDescription": "经源码核对的英文 Automic Vault 2.9.0 CLI 手册，涵盖 scan、doctor、save、inject、bless 和 harden。",
        "blogDescription": "关于软件包、扩展、凭据和本地执行事件的开发者安全指南与分析。",
        "sourceDescription": "Apache-2.0 源代码、标签版本、实现历史和公开问题跟踪。",
        "securityDescription": "公布当前安全联系方式、首选语言、规范地址和到期日期。",
        "facts": "关键信息",
        "platform": "平台：macOS",
        "release": "当前文档版本：2.9.0",
        "license": "许可证：Apache License 2.0",
        "pricing": "价格：免费开源软件",
        "founder": "创始人：Homebrew 作者 Max Howell",
        "contact": "联系方式",
        "securityReports": "安全报告",
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def enabled_locales() -> list[Locale]:
    data = load_json(LOCALES_PATH)
    locales = []
    for item in data["locales"]:
        if not item.get("enabled", False):
            continue
        locales.append(
            Locale(
                code=item["code"],
                slug=item["slug"],
                html_lang=item["htmlLang"],
                hreflang=item["hreflang"],
                display_name=item["displayName"],
                native_name=item["nativeName"],
                browser_languages=tuple(item.get("browserLanguages", [])),
                enabled=True,
            )
        )
    return locales


def non_default_locales() -> list[Locale]:
    return [locale for locale in enabled_locales() if locale.code != "en"]


def locale_path(path: str, locale: Locale | None) -> str:
    if locale is None or locale.code == "en":
        return path
    if path == "/":
        return f"/{locale.slug}/"
    return f"/{locale.slug}{path}"


def route_file(path: str, locale: Locale) -> Path:
    route = locale_path(path, locale).strip("/")
    if not route:
        return SITE_DIR / "index.html"
    return SITE_DIR / route / "index.html"


def rel_root(path: str, locale: Locale) -> str:
    depth = 0 if path == "/" else len(path.strip("/").split("/"))
    if locale.code != "en":
        depth += 1
    return "../" * depth


def href(path: str, locale: Locale | None = None) -> str:
    return SITE_ORIGIN + locale_path(path, locale)


def package_href(locale: Locale | None = None) -> str:
    return PACKAGE_ORIGIN + locale_path("/", locale)


def ui_copy(locale_code: str) -> dict[str, str]:
    return UI_COPY.get(locale_code, UI_COPY["en"])


def alternate_link_block(path: str, locales: list[Locale], indent: str = "  ") -> str:
    links = [f'{indent}<link rel="alternate" hreflang="en" href="{href(path)}">']
    for locale in locales:
        if locale.code == "en":
            continue
        links.append(f'{indent}<link rel="alternate" hreflang="{locale.hreflang}" href="{href(path, locale)}">')
    links.append(f'{indent}<link rel="alternate" hreflang="x-default" href="{href(path)}">')
    return "\n".join(links)


def language_links(path: str, current: Locale, locales: list[Locale]) -> str:
    ui = ui_copy(current.code)
    links = [f'<a href="{html.escape(locale_path(path, locale if locale.code != "en" else None))}" lang="{html.escape(locale.html_lang)}">{html.escape(locale.native_name)}</a>' for locale in locales]
    return f'<nav class="language-links" aria-label="{html.escape(ui["languageVersionsAria"], quote=True)}">{" ".join(links)}</nav>'


def translated_page_records() -> list[dict[str, Any]]:
    data = load_json(STATIC_PATH)
    records = [copy.deepcopy(item) for item in data["pages"]]
    seed = records[0]
    aliases = data.get("aliases", {})
    for path, topic_key in aliases.items():
        translations = TOPICS[topic_key]
        records.append({
            "path": path,
            "source": path.strip("/") + "/index.html",
            "dateModified": seed.get("dateModified", "2026-05-24"),
            "translations": translations,
        })
    return records


TITLE_SUFFIX: dict[str, str] = {
    "ja": " | AI エージェントと開発ツールの保護",
    "de": " | Schutz für AI-Agents und Entwickler-Tools",
    "fr": " | Protection des agents IA et outils développeur",
    "zh-Hans": " | AI 代理与开发工具安全",
}


DESCRIPTION_ADDENDUM: dict[str, str] = {
    "ja": "Homebrew ツール、CLI シークレット、承認ゲートを Mac 上でローカルに制御します。",
    "de": "Kontrolliere Homebrew-Tools, CLI-Secrets und Approval Gates lokal auf dem Mac.",
    "fr": "Contrôlez localement sur Mac les outils Homebrew, les secrets CLI et les portes d'approbation.",
    "zh-Hans": "在本地 Mac 上控制 Homebrew 工具、CLI 密钥和审批门。",
}


SUPPORT_SECTIONS: dict[str, list[list[str]]] = {
    "ja": [
        ["ローカル実行境界", "Automic Vault は、エージェントが読めるファイルと、承認されたツールだけが受け取る認証情報を分けます。モデルの指示ではなく、Mac 上の実行経路で制御します。"],
        ["Homebrew と CLI", "多くの開発ツールは Homebrew、npm、PyPI、クラウド CLI から入ります。Vault は、そのツールが作る認証情報ファイルや危険な操作を検出して、必要な場所に承認を置きます。"],
        ["次の手順", "まずスキャナーで平文の露出を確認し、対応済みのシークレットを保護されたローカル保存に移し、Automic Vault を起動したまま新しい hazard 通知を受け取ります。"],
        ["インストール後の変化", "既存の CLI は使い続けられます。ただし、シークレットはエージェントが読める設定ファイルではなく、承認された実行だけが受け取るローカル境界の中に移ります。"],
        ["中央の vault との違い", "1Password や HashiCorp Vault はシークレットの管理元として使えます。Automic Vault は、その値が Mac 上のツールへ渡される瞬間を制御します。"],
        ["関連ページ", "ドキュメント、ダウンロード、シークレットスキャナー、パッケージカタログを確認すると、検出からハードニング、承認、継続監視までの流れが分かります。"],
        ["継続監視", "新しいパッケージ、古いツール、再作成された設定ファイルは、最初の修正後にも危険を戻す可能性があります。Automic Vault は新しい hazard を知らせます。"],
        ["信頼の手がかり", "公開リポジトリ、セキュリティページ、ライセンス、Max Howell の Homebrew 背景を確認できます。ローカルのセキュリティ境界は、検証可能であるべきです。"],
        ["使う場面", "エージェントにリポジトリを任せる前、クラウド CLI を使う前、npm publish や gh release のような権限の強いコマンドを許可する前に使います。"],
    ],
    "de": [
        ["Lokale Laufzeitgrenze", "Automic Vault trennt Dateien, die ein Agent lesen kann, von Credentials, die nur genehmigte Tools erhalten. Die Kontrolle sitzt im Ausführungspfad auf dem Mac, nicht nur in einer Agent-Anweisung."],
        ["Homebrew und CLIs", "Viele Entwicklerwerkzeuge kommen über Homebrew, npm, PyPI und Cloud-CLIs. Vault erkennt Credential-Dateien und riskante Aktionen, die diese Tools hinterlassen, und setzt Freigaben an die passende Stelle."],
        ["Nächste Schritte", "Starte zuerst den Scanner, verschiebe unterstützte Secrets in geschützten lokalen Speicher und lasse Automic Vault laufen, damit neue Hazard-Hinweise sofort sichtbar bleiben."],
        ["Was sich nach der Installation ändert", "Die bekannten CLIs bleiben nutzbar. Der Unterschied ist, dass Secrets nicht mehr als einfache Konfigurationsdateien herumliegen, sondern nur an die genehmigte Ausführung übergeben werden, die sie wirklich braucht."],
        ["Zusammenspiel mit zentralen Vaults", "1Password, HashiCorp Vault und Cloud-Secret-Systeme können weiter die Quelle der Wahrheit bleiben. Automic Vault schützt den lokalen Moment, in dem ein Mac-Tool diese Werte verwenden will."],
        ["Weiterführende Seiten", "Dokumentation, Download, Secret Scanner und Paketkatalog zeigen den Weg von Erkennung zu Härtung, Approval Gates und laufender Überwachung der Entwickler-Maschine."],
        ["Laufende Überwachung", "Neue Pakete, veraltete Tools und neu erzeugte Konfigurationsdateien können nach der ersten Bereinigung wieder Risiken schaffen. Automic Vault bleibt aktiv und meldet frische Hazards."],
        ["Vertrauenshinweise", "Öffentliches Repository, Sicherheitsseite, Lizenz und der Homebrew-Hintergrund von Max Howell sind verlinkt. Eine lokale Sicherheitsgrenze sollte überprüfbar sein."],
        ["Wann einsetzen", "Nutze Automic Vault vor Agent-Läufen in Repositories, vor Cloud-CLI-Arbeit und bevor Befehle wie npm publish, gh release oder Infrastrukturänderungen echte Berechtigungen ausgeben."],
    ],
    "fr": [
        ["Limite d'exécution locale", "Automic Vault sépare les fichiers lisibles par un agent des identifiants transmis uniquement aux outils approuvés. Le contrôle vit dans le chemin d'exécution sur Mac, pas seulement dans une consigne d'agent."],
        ["Homebrew et CLI", "Beaucoup d'outils développeur arrivent par Homebrew, npm, PyPI et les CLI cloud. Vault détecte les fichiers d'identifiants et les actions risquées laissés par ces outils, puis place l'approbation au bon endroit."],
        ["Étapes suivantes", "Lancez d'abord le scanner, déplacez les secrets pris en charge vers un stockage local protégé et gardez Automic Vault actif pour recevoir les nouveaux avis de danger."],
        ["Ce qui change après installation", "Les CLI habituelles continuent de fonctionner. La différence est que les secrets ne restent pas dans de simples fichiers de configuration; ils sont transmis seulement à l'exécution approuvée qui en a besoin."],
        ["Avec un coffre central", "1Password, HashiCorp Vault et les systèmes cloud peuvent rester la source de vérité. Automic Vault protège le moment local où un outil Mac veut utiliser ces valeurs."],
        ["Pages liées", "Documentation, téléchargement, scanner de secrets et catalogue de paquets montrent le parcours complet: détection, durcissement, approbation et surveillance continue du poste développeur."],
        ["Surveillance continue", "Nouveaux paquets, outils obsolètes et fichiers de configuration recréés peuvent ramener des risques après la première correction. Automic Vault reste actif et signale les nouveaux dangers."],
        ["Signaux de confiance", "Le dépôt public, la page sécurité, la licence et le contexte Homebrew de Max Howell sont liés. Une limite de sécurité locale doit pouvoir être vérifiée."],
        ["Quand l'utiliser", "Utilisez Automic Vault avant les exécutions d'agents dans un dépôt, avant le travail avec les CLI cloud et avant les commandes comme npm publish, gh release ou les mutations d'infrastructure."],
    ],
    "zh-Hans": [
        ["本地运行边界", "Automic Vault 将代理可读取的文件与只提供给已批准工具的凭据分开。控制发生在 Mac 的执行路径上，而不是只依赖代理提示词。"],
        ["Homebrew 与 CLI", "许多开发工具来自 Homebrew、npm、PyPI 和云 CLI。Vault 会检测这些工具留下的凭据文件和高风险操作，并把审批放到实际执行位置。"],
        ["下一步", "先运行扫描器检查明文暴露，将支持的密钥移入受保护的本地存储，并保持 Automic Vault 运行，以便及时收到新的 hazard 通知。"],
        ["安装后的变化", "熟悉的 CLI 仍可继续使用。区别在于密钥不再作为容易读取的配置文件留在磁盘上，而是只交给真正需要它的已批准执行。"],
        ["与中心化 vault 配合", "1Password、HashiCorp Vault 和云端密钥系统仍可作为真实来源。Automic Vault 保护的是本地 Mac 工具使用这些值的那一刻。"],
        ["相关页面", "文档、下载、密钥扫描器和软件包目录展示完整流程：发现暴露、加固工具、加入审批门，并持续监控开发机器。"],
        ["持续监控", "新的软件包、过时工具和重新生成的配置文件可能在首次修复后重新带来风险。Automic Vault 会保持运行并提示新的 hazard。"],
        ["可信线索", "公开仓库、安全页面、许可证以及 Max Howell 的 Homebrew 背景都可查看。本地安全边界应该能够被验证。"],
        ["何时使用", "在让代理处理仓库之前、使用云 CLI 之前，以及允许 npm publish、gh release 或基础设施变更等高权限命令之前使用 Automic Vault。"],
    ],
}

def normalized_title(title: str, locale: Locale) -> str:
    if locale.code == "en":
        return title
    if len(title) >= 34 or "|" in title:
        return title
    return title + TITLE_SUFFIX[locale.code]


def normalized_description(description: str, locale: Locale) -> str:
    if locale.code == "en" or len(description) >= 105:
        return description
    addendum = DESCRIPTION_ADDENDUM[locale.code]
    if addendum in description:
        return description
    return f"{description} {addendum}"


def expanded_sections(translations: dict[str, Any], locale: Locale) -> list[list[str]]:
    sections = [list(item) for item in translations.get("sections", [])]
    seen = {title for title, _ in sections}
    for title, body in SUPPORT_SECTIONS.get(locale.code, []):
        if len(sections) >= 11:
            break
        if title in seen:
            continue
        sections.append([title, body])
        seen.add(title)
    return sections


def render_page(record: dict[str, Any], locale: Locale, locales: list[Locale]) -> str:
    path = record["path"]
    t = record["translations"][locale.code]
    ui = ui_copy(locale.code)
    root = rel_root(path, locale)
    canonical = href(path, locale)
    page_title = normalized_title(t["title"], locale)
    page_description = normalized_description(t["description"], locale)
    section_markup = "\n".join(
        f"""      <section class="i18n-section" aria-labelledby="section-{index}">
        <h2 id="section-{index}">{html.escape(title)}</h2>
        <p>{html.escape(body)}</p>
      </section>"""
        for index, (title, body) in enumerate(expanded_sections(t, locale), start=1)
    )
    download_gallery = ""
    if path == "/download/":
        image_alts = DOWNLOAD_IMAGE_ALTS[locale.code]
        download_gallery = f"""
      <section class="download-gallery" aria-label="{html.escape(t["h1"], quote=True)}">
        <figure class="download-gallery-primary">
          <img src="/assets/av-approve-gate.png" alt="{html.escape(image_alts[0], quote=True)}" width="1212" height="1090" loading="eager" decoding="async">
        </figure>
        <figure>
          <img src="/assets/access-levels.png" alt="{html.escape(image_alts[1], quote=True)}" width="1944" height="1380" loading="lazy" decoding="async">
        </figure>
        <figure>
          <img src="/assets/secret-use-log.webp" alt="{html.escape(image_alts[2], quote=True)}" width="1944" height="1380" loading="lazy" decoding="async">
        </figure>
      </section>
"""
    hero_actions = f"""          <a class="button primary" href="/Automic%20Vault.dmg">{html.escape(ui["download"])}</a>
          <a class="button secondary" href="/docs/">{html.escape(ui["docs"])}</a>"""
    language_nav = language_links(path, locale, locales)
    return f"""<!DOCTYPE html>
<html lang="{html.escape(locale.html_lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(page_description, quote=True)}">
  <meta name="robots" content="index,follow">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Automic Vault">
  <meta property="og:title" content="{html.escape(page_title, quote=True)}">
  <meta property="og:description" content="{html.escape(page_description, quote=True)}">
  <meta property="og:url" content="{html.escape(canonical, quote=True)}">
  <meta property="og:image" content="{SITE_ORIGIN}/preview.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(page_title, quote=True)}">
  <meta name="twitter:description" content="{html.escape(page_description, quote=True)}">
  <meta name="twitter:image" content="{SITE_ORIGIN}/preview.jpg">
  <link rel="canonical" href="{html.escape(canonical, quote=True)}">
{alternate_link_block(path, locales)}
  <link rel="alternate" type="text/plain" title="llms.txt" href="{locale_path('/llms.txt', locale)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&amp;family=Geist+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
  <link rel="icon" href="{root}favicon.ico?v=5" sizes="16x16 32x32 48x48">
  <link rel="icon" href="{root}favicon-dark.svg?v=5" type="image/svg+xml" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="{root}favicon.svg?v=5" type="image/svg+xml" media="(prefers-color-scheme: light)">
  <link rel="mask-icon" href="{root}safari-pinned-tab.svg?v=5" color="#ffffff" media="(prefers-color-scheme: dark)">
  <link rel="mask-icon" href="{root}safari-pinned-tab.svg?v=5" color="#111111" media="(prefers-color-scheme: light)">
  <link rel="apple-touch-icon" href="{root}apple-touch-icon.png?v=3">
  <link rel="stylesheet" href="{root}styles.css?v=128">
  <link rel="stylesheet" href="{root}landing-pages.css?v=5">
{GOOGLE_ANALYTICS_TAG}
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "url": "{canonical}",
    "name": {json.dumps(page_title, ensure_ascii=False)},
    "headline": {json.dumps(t["h1"], ensure_ascii=False)},
    "description": {json.dumps(page_description, ensure_ascii=False)},
    "inLanguage": "{locale.html_lang}",
    "image": "{SITE_ORIGIN}/preview.jpg",
    "isPartOf": {{"@type": "WebSite", "name": "Automic Vault", "url": "{SITE_ORIGIN}/"}}
  }}
  </script>
</head>
<body>
  <div class="scroll-meter" aria-hidden="true"><span></span></div>
  <div class="seo-shell">
    <header class="seo-masthead" id="top">
      <a class="brand" href="{locale_path('/', locale)}" aria-label="{html.escape(ui["brandHomeAria"], quote=True)}">
        <img class="brand-mark" src="/assets/icon@2x.webp?v=3" alt="Automic Vault icon" width="54" height="54">
        <img class="brand-wordmark" src="/assets/wordmark.webp" alt="Automic Vault" width="996" height="257">
      </a>
      <nav class="seo-nav" aria-label="{html.escape(ui["mainNavigationAria"], quote=True)}">
        <a href="/Automic%20Vault.dmg">{html.escape(ui["download"])}</a>
        <a href="{package_href(locale)}">{html.escape(ui["packages"])}</a>
        <a href="/blog/">Blog</a>
        <a href="{locale_path('/about/', locale)}">{html.escape(ui["about"])}</a>
        <a href="https://github.com/automic-vault/automic-vault">GitHub</a>
      </nav>
    </header>

    <main class="landing-main landing-page-main">
      <section class="poster-hero landing-page-hero" aria-labelledby="hero-title">
        <div class="poster-hero-copy">
          <p class="eyebrow">{html.escape(t.get("kicker", "Automic Vault"))}</p>
          <h1 id="hero-title">{html.escape(t["h1"])}</h1>
          <p class="poster-lede">{html.escape(t.get("lede", t["description"]))}</p>
        </div>

        <div class="poster-hero-foot">
          <div class="hero-actions">
{hero_actions}
          </div>
        </div>
      </section>
{download_gallery}
{section_markup}

      <section class="closing-cta landing-page-cta" aria-labelledby="final-title">
        <p class="eyebrow">Automic Vault</p>
        <h2 id="final-title">{html.escape(t["h1"])}</h2>
        <div class="hero-actions">
          <a class="button primary" href="/Automic%20Vault.dmg">{html.escape(ui["download"])}</a>
          <a class="button secondary" href="/docs/">{html.escape(ui["docs"])}</a>
          <a class="button text" href="{package_href(locale)}">{html.escape(ui["packages"])}</a>
        </div>
      </section>
    </main>

    <footer class="seo-footer">
      <p>&copy; 2026 Automic Vault.</p>
      <nav class="footer-links" aria-label="Footer navigation">
        <a href="{locale_path('/', locale)}">{html.escape(ui["website"])}</a>
        <a href="{locale_path('/about/', locale)}">{html.escape(ui["about"])}</a>
        <a href="/blog/">Blog</a>
        <a href="{locale_path('/privacy/', locale)}">{html.escape(ui["privacy"])}</a>
        <a href="{locale_path('/terms/', locale)}">{html.escape(ui["terms"])}</a>
        <a href="https://github.com/automic-vault/automic-vault">GitHub</a>
      </nav>
    </footer>
  </div>

  {language_nav}
  <script src="{root}i18n.js" defer></script>
</body>
</html>
"""


def render_llms(locale: Locale, records: list[dict[str, Any]]) -> str:
    ui = ui_copy(locale.code)
    copy = LLMS_COPY[locale.code]
    records_by_path = {record["path"]: record for record in records}
    page_lines = []
    for path in ("/", "/download/", "/about/", "/privacy/", "/terms/"):
        translation = records_by_path[path]["translations"][locale.code]
        page_lines.append(f'- [{translation["title"]}]({href(path, locale)}): {translation["description"]}')
    page_lines[2:2] = [
        f'- [{ui["docs"]}]({href("/docs/")}): {copy["docsDescription"]}',
        f'- [{ui["packages"]}]({package_href(locale)}): {copy["packagesDescription"]}',
        f'- [Blog]({href("/blog/")}): {copy["blogDescription"]}',
    ]
    page_lines.extend([
        f'- [GitHub](https://github.com/automic-vault/automic-vault): {copy["sourceDescription"]}',
        f'- [{ui["security"]}]({href("/.well-known/security.txt")}): {copy["securityDescription"]}',
    ])
    lines = [
        "# Automic Vault",
        f'> {copy["summary"]}',
        f'## {copy["pages"]}',
        *page_lines,
        f'## {copy["facts"]}',
        f'- {copy["platform"]}',
        f'- {copy["release"]}',
        f'- {copy["license"]}',
        f'- {copy["pricing"]}',
        f'- {copy["founder"]}',
        f'## {copy["contact"]}',
        f'- {ui["website"]}: {href("/", locale)}',
        '- GitHub: https://github.com/automic-vault/automic-vault',
        f'- {copy["securityReports"]}: https://github.com/automic-vault/automic-vault/issues',
    ]
    return "\n\n".join(lines) + "\n"


def render_i18n_js(locales: list[Locale]) -> str:
    data = [
        {
            "code": locale.code,
            "slug": locale.slug,
            "nativeName": locale.native_name,
            "languages": list(locale.browser_languages),
            "suggestionAria": ui_copy(locale.code)["languageSuggestionAria"],
            "suggestionText": ui_copy(locale.code)["languageSuggestionText"],
            "dismissLabel": ui_copy(locale.code)["dismissLanguageSuggestion"],
        }
        for locale in locales
        if locale.code != "en"
    ]
    return f"""(() => {{
  const locales = {json.dumps(data, ensure_ascii=False)};
  const dismissedKey = "av-i18n-dismissed";
  if (localStorage.getItem(dismissedKey) === "1") return;
  const path = window.location.pathname;
  if (/^\\/(ja|de|fr|zh-hans)(\\/|$)/.test(path)) return;
  const languages = navigator.languages || [navigator.language || ""];
  const match = languages
    .map((item) => String(item).toLowerCase())
    .map((item) => locales.find((locale) => locale.languages.includes(item) || locale.languages.includes(item.split("-")[0])))
    .find(Boolean);
  if (!match) return;
  const localized = "/" + match.slug + (path === "/" ? "/" : path);
  fetch(localized, {{ method: "HEAD" }})
    .then((response) => {{
      if (!response.ok) return;
      const banner = document.createElement("aside");
      banner.className = "i18n-suggestion";
      banner.setAttribute("aria-label", match.suggestionAria);
      const link = document.createElement("a");
      link.href = localized;
      link.textContent = match.suggestionText;
      const button = document.createElement("button");
      button.type = "button";
      button.setAttribute("aria-label", match.dismissLabel);
      button.textContent = "×";
      button.addEventListener("click", () => {{
        localStorage.setItem(dismissedKey, "1");
        banner.remove();
      }});
      banner.append(link, button);
      document.body.appendChild(banner);
    }})
    .catch(() => {{}});
}})();
"""


def patch_english_page(path: str, locales: list[Locale], check: bool, failures: list[str]) -> None:
    file = route_file(path, Locale("en", "", "en", "en", "English", "English", ("en",), True))
    if not file.exists():
        failures.append(f"missing English source page: {file}")
        return
    text = file.read_text(encoding="utf-8")
    canonical_match = re.search(r'<link rel="canonical" href="https://www\.automicvault\.com([^"]*)">', text)
    if not canonical_match:
        failures.append(f"missing canonical in {file}")
        return
    route = canonical_match.group(1) or "/"
    block = alternate_link_block(route, locales)
    text = re.sub(r'\n  <link rel="alternate" hreflang="[^"]+" href="[^"]+">', "", text)
    if block not in text:
        text = text.replace(canonical_match.group(0), canonical_match.group(0) + "\n" + block)
    language_block = language_links(route, Locale("en", "", "en", "en", "English", "English", ("en",), True), locales)
    if "class=\"language-links\"" not in text and "class=\"brew-languages\"" not in text:
        text = text.replace("</body>", f"  {language_block}\n</body>")
    if 'src="/i18n.js"' not in text:
        text = text.replace("</body>", '  <script src="/i18n.js" defer></script>\n</body>')
    if check:
        current = file.read_text(encoding="utf-8")
        if current != text:
            failures.append(f"stale i18n head/body metadata: {file}")
    else:
        file.write_text(text, encoding="utf-8")


def check_curated_home_page(output: Path, locale: Locale, locales: list[Locale], failures: list[str]) -> None:
    if not output.exists():
        failures.append(f"missing curated localized homepage: {output}")
        return

    text = output.read_text(encoding="utf-8")
    required = [
        f'<html lang="{locale.html_lang}">',
        '<body class="brew-home">',
        'class="brew-hero-capture"',
        'class="brew-access"',
        'id="terminal-security"',
        f'<link rel="canonical" href="{href("/", locale)}">',
        f'<link rel="alternate" type="text/plain" title="llms.txt" href="{locale_path("/llms.txt", locale)}">',
        'class="brew-languages"',
        'src="/i18n.js"',
    ]
    required.extend(line.strip() for line in alternate_link_block("/", locales).splitlines())
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        failures.append(f"stale curated localized homepage metadata: {output}")


def sitemap_entry(loc: str, lastmod: str, path: str | None, locales: list[Locale]) -> str:
    body = [f"  <url>", f"    <loc>{html.escape(loc)}</loc>", f"    <lastmod>{lastmod}</lastmod>"]
    if path:
        body.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{href(path)}" />')
        for locale in locales:
            if locale.code == "en":
                continue
            body.append(f'    <xhtml:link rel="alternate" hreflang="{locale.hreflang}" href="{href(path, locale)}" />')
        body.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{href(path)}" />')
    body.append("  </url>")
    return "\n".join(body)


def render_sitemap(records: list[dict[str, Any]], locales: list[Locale]) -> str:
    entries: list[str] = []
    for record in records:
        path = record["path"]
        lastmod = record.get("dateModified", "2026-05-24")
        entries.append(sitemap_entry(href(path), lastmod, path, locales))
        for locale in locales:
            if locale.code == "en":
                continue
            entries.append(sitemap_entry(href(path, locale), lastmod, path, locales))
    preserved = [
        ("https://www.automicvault.com/docs/", "2026-07-27"),
        ("https://www.automicvault.com/blog/", "2026-08-14"),
        ("https://www.automicvault.com/blog/automic-vault-vs-doppler/", "2026-08-14"),
        ("https://www.automicvault.com/blog/automic-vault-vs-bitwarden/", "2026-08-14"),
        ("https://www.automicvault.com/blog/automic-vault-vs-1password/", "2026-08-14"),
        ("https://www.automicvault.com/blog/best-aws-credential-manager/", "2026-08-05"),
        ("https://www.automicvault.com/blog/prevent-keyv-npm-worm/", "2026-08-04"),
        ("https://www.automicvault.com/blog/mac-security-best-practices-for-agents/", "2026-07-16"),
        ("https://www.automicvault.com/blog/bringing-macos-security-to-the-terminal/", "2026-07-12"),
        ("https://www.automicvault.com/blog/prevent-nx-console-vscode-compromise/", "2026-05-21"),
        ("https://www.automicvault.com/blog/prevent-github-vscode-extension-breach/", "2026-05-21"),
        ("https://www.automicvault.com/blog/prevent-durabletask-pypi-compromise/", "2026-05-20"),
        ("https://www.automicvault.com/blog/prevent-tanstack-npm-compromise/", "2026-05-15"),
        ("https://www.automicvault.com/blog/prevent-node-ipc-npm-backdoor/", "2026-05-15"),
        ("https://www.automicvault.com/blog/prevent-bitwarden-cli-npm-compromise/", "2026-04-23"),
        ("https://www.automicvault.com/blog/prevent-litellm-pypi-compromise/", "2026-03-25"),
        ("https://www.automicvault.com/llms.txt", "2026-07-28"),
        ("https://www.automicvault.com/llms-full.txt", "2026-07-28"),
        ("https://www.automicvault.com/.well-known/security.txt", "2026-07-28"),
    ]
    entries.extend(sitemap_entry(loc, lastmod, None, locales) for loc, lastmod in preserved)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(entries) + "\n</urlset>\n"


def generate(check: bool = False) -> int:
    locales = enabled_locales()
    locale_codes = {locale.code for locale in locales}
    records = translated_page_records()
    failures: list[str] = []
    for record in records:
        missing = locale_codes - {"en"} - set(record.get("translations", {}).keys())
        if missing:
            failures.append(f"{record['path']} missing translations: {', '.join(sorted(missing))}")
            continue
        english_locale = next(locale for locale in locales if locale.code == "en")
        english_output = route_file(record["path"], english_locale)
        if "en" in record.get("translations", {}):
            expected_english = render_page(record, english_locale, locales)
            if check:
                if not english_output.exists() or english_output.read_text(encoding="utf-8") != expected_english:
                    failures.append(f"stale generated English page: {english_output}")
            else:
                english_output.parent.mkdir(parents=True, exist_ok=True)
                english_output.write_text(expected_english, encoding="utf-8")
        else:
            patch_english_page(record["path"], locales, check, failures)
        for locale in non_default_locales():
            output = route_file(record["path"], locale)
            if record["path"] == "/":
                check_curated_home_page(output, locale, locales, failures)
                continue
            expected = render_page(record, locale, locales)
            if check:
                if not output.exists() or output.read_text(encoding="utf-8") != expected:
                    failures.append(f"stale localized page: {output}")
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(expected, encoding="utf-8")
    for locale in non_default_locales():
        output = SITE_DIR / locale.slug / "llms.txt"
        expected = render_llms(locale, records)
        if check:
            if not output.exists() or output.read_text(encoding="utf-8") != expected:
                failures.append(f"stale localized llms.txt: {output}")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(expected, encoding="utf-8")
    expected_js = render_i18n_js(locales)
    if check:
        if not I18N_SCRIPT.exists() or I18N_SCRIPT.read_text(encoding="utf-8") != expected_js:
            failures.append(f"stale i18n browser helper: {I18N_SCRIPT}")
    else:
        I18N_SCRIPT.write_text(expected_js, encoding="utf-8")
    expected_sitemap = render_sitemap(records, locales)
    if check:
        if not SITEMAP_PATH.exists() or SITEMAP_PATH.read_text(encoding="utf-8") != expected_sitemap:
            failures.append(f"stale localized sitemap: {SITEMAP_PATH}")
    else:
        SITEMAP_PATH.write_text(expected_sitemap, encoding="utf-8")
    if failures:
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate localized static website pages.")
    parser.add_argument("--check", action="store_true", help="Validate generated localized static pages.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    import os
    os.chdir(root)
    return generate(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
