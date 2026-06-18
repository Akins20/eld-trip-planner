import '@testing-library/jest-dom';

// jsdom does not implement scrollIntoView; stub it so the Tour can run in tests.
if (typeof Element !== 'undefined' && !Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => {};
}
