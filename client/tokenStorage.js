const tokenStorageKey = "token";
const httpOnlyCookieModeKey = "httpOnlyAuthCookie";

function getBasePath() {
  // This relies on the fact that flanotes always has a correctly formatted relative path set in <base> tag
  return document.querySelector('base').getAttribute('href')
}

function getCookieString(token = "") {
  const basePath = getBasePath();
  return `${tokenStorageKey}=${token}; Path=${basePath}; SameSite=Strict`;
}

export function storeToken(token, persist = false) {
  if (!isManagedCookieMode()) {
    document.cookie = getCookieString(token);
  }
  sessionStorage.setItem(tokenStorageKey, token);
  if (persist === true) {
    localStorage.setItem(tokenStorageKey, token);
  }
}

export function getStoredToken() {
  return sessionStorage.getItem(tokenStorageKey);
}

export function loadStoredToken() {
  const token = localStorage.getItem(tokenStorageKey);
  if (token != null) {
    storeToken(token, false);
  }
}

export function clearStoredToken() {
  sessionStorage.removeItem(tokenStorageKey);
  localStorage.removeItem(tokenStorageKey);
  document.cookie =
    getCookieString() + "; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  localStorage.removeItem(httpOnlyCookieModeKey);
}

export function isCurrentTokenStored() {
  const localToken = localStorage.getItem(tokenStorageKey);
  if (localToken == null) {
    return false;
  }
  const sessionToken = sessionStorage.getItem(tokenStorageKey);
  return localToken === sessionToken;
}

export function setManagedCookieMode(enabled) {
  if (enabled) {
    localStorage.setItem(httpOnlyCookieModeKey, "true");
  } else {
    localStorage.removeItem(httpOnlyCookieModeKey);
  }
}

export function isManagedCookieMode() {
  return localStorage.getItem(httpOnlyCookieModeKey) === "true";
}
