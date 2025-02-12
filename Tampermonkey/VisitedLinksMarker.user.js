// ==UserScript==
// @name                Visited Links Marker
// @name:zh-CN          访问过的链接标记器
// @name:zh-TW          用自訂顏色標記已訪問的連結
// @name:ja             訪問済みリンクマーカー
// @name:ko             방문한 링크 마커
// @name:ru             Маркер посещенных ссылок
// @namespace           hugepower.VisitedLite
// @description         Mark visited links with a customizable color.
// @description:zh-CN   用自定义颜色标记已访问的链接。
// @description:zh-TW   用自訂顏色標記已訪問的連結
// @description:ja      訪問済みリンクをカスタマイズ可能な色でマークします
// @description:ko      방문한 링크를 사용자 정의 색상으로 표시합니다
// @description:ru      Помечает посещенные ссылки настраиваемым цветом
// @author              hugepower
// @version             1.1
// @match               *://*/*
// @run-at              document-start
// @grant               GM_addStyle
// @grant               GM_registerMenuCommand
// @grant               GM_setValue
// @grant               GM_getValue
// @license             MIT
// ==/UserScript==

(() => {
  //// Config
  const VISITED_COLOR = 'LightCoral'; // Custom color for visited links
  const INCLUDED_SITES = []; // Sites where script will be applied

  //// CSS rule for visited links
  const VISITED_CSS = `a:visited, a:visited * { color: ${VISITED_COLOR} !important; }`;

  //// Multi-language support for menu items
  const getMenuLabels = () => {
    const userLang = navigator.language || navigator.userLanguage;

    const translations = {
      en: {
        allPages: 'Mode: Apply on all pages',
        includedSites: 'Mode: Apply only on included sites',
        switchAlert: 'Mode switched to: ',
      },
      'zh-CN': {
        allPages: '模式：在所有页面上启用',
        includedSites: '模式：仅启用在指定网站',
        switchAlert: '模式已切换为：',
      },
      'zh-TW': {
        allPages: '模式：在所有頁面上啟用',
        includedSites: '模式：僅啟用在指定網站',
        switchAlert: '模式已切換為：',
      },
      ja: {
        allPages: 'モード：すべてのページで適用',
        includedSites: 'モード：特定のサイトでのみ適用',
        switchAlert: 'モードが切り替わりました：',
      },
      ko: {
        allPages: '모드: 모든 페이지에 적용',
        includedSites: '모드: 포함된 사이트에만 적용',
        switchAlert: '모드가 전환되었습니다: ',
      },
      ru: {
        allPages: 'Режим: Применять ко всем страницам',
        includedSites: 'Режим: Применять только на выбранных сайтах',
        switchAlert: 'Режим переключен на: ',
      },
    };

    return translations[userLang] || translations.en;
  };

  const menuLabels = getMenuLabels();

  //// Mode Switching Logic
  const switchMode = (mode) => {
    GM_setValue('mode', mode);
    alert(menuLabels.switchAlert + mode);
    location.reload();
  };

  const applyVisitedColor = () => {
    const mode = GM_getValue('mode', 'allPages');
    const currentURL = document.documentURI;

    if (
      mode === 'allPages' ||
      (mode === 'includedSites' && INCLUDED_SITES.some((site) => currentURL.includes(site)))
    ) {
      GM_addStyle(VISITED_CSS); // Apply the custom style for visited links
    }
  };

  //// Menu Commands
  GM_registerMenuCommand(menuLabels.allPages, () => switchMode('allPages'));
  GM_registerMenuCommand(menuLabels.includedSites, () => switchMode('includedSites'));

  //// Apply styles immediately at document-start
  applyVisitedColor();
})();
