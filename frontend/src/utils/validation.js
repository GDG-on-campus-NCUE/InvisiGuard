/**
 * Client-side validation utilities for InvisiGuard
 * Provides pre-submission validation to catch errors before API calls
 */

const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/jpg'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes
const ALPHA_MIN = 0.1;
const ALPHA_MAX = 5.0;
const MAX_TEXT_LENGTH = 240;

/**
 * Validate image file type and size
 * @param {File} file - The file to validate
 * @returns {{valid: boolean, error?: string}} Validation result
 */
export function validateImageFile(file) {
  if (!file) {
    return { valid: false, error: 'No file selected' };
  }

  // Check file type
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: `Invalid file format. Only PNG and JPG images are supported. Got: ${file.type}`
    };
  }

  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    return {
      valid: false,
      error: `File size (${sizeMB}MB) exceeds maximum allowed size of 10MB`
    };
  }

  return { valid: true };
}

/**
 * Validate watermark text
 * @param {string} text - The text to validate
 * @returns {{valid: boolean, error?: string}} Validation result
 */
export function validateWatermarkText(text) {
  if (!text || text.trim().length === 0) {
    return { valid: false, error: 'Watermark text cannot be empty' };
  }

  if (text.length > MAX_TEXT_LENGTH) {
    return {
      valid: false,
      error: `Watermark text exceeds maximum length of ${MAX_TEXT_LENGTH} characters`
    };
  }

  return { valid: true };
}

/**
 * Validate alpha (strength) value
 * @param {number} alpha - The alpha value to validate
 * @returns {{valid: boolean, error?: string}} Validation result
 */
export function validateAlpha(alpha) {
  const alphaNum = Number(alpha);
  
  if (isNaN(alphaNum)) {
    return { valid: false, error: 'Alpha value must be a number' };
  }

  if (alphaNum < ALPHA_MIN || alphaNum > ALPHA_MAX) {
    return {
      valid: false,
      error: `Alpha value must be between ${ALPHA_MIN} and ${ALPHA_MAX}. Got: ${alphaNum}`
    };
  }

  return { valid: true };
}

/**
 * Validate embed request (comprehensive check)
 * @param {File} file - Image file
 * @param {string} text - Watermark text
 * @param {number} alpha - Strength value
 * @returns {{valid: boolean, errors: string[]}} Validation result with all errors
 */
export function validateEmbedRequest(file, text, alpha) {
  const errors = [];

  const fileValidation = validateImageFile(file);
  if (!fileValidation.valid) {
    errors.push(fileValidation.error);
  }

  const textValidation = validateWatermarkText(text);
  if (!textValidation.valid) {
    errors.push(textValidation.error);
  }

  const alphaValidation = validateAlpha(alpha);
  if (!alphaValidation.valid) {
    errors.push(alphaValidation.error);
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate extract request (two files required)
 * @param {File} originalFile - Original embedded image
 * @param {File} suspectFile - Suspect image to compare
 * @returns {{valid: boolean, errors: string[]}} Validation result
 */
export function validateExtractRequest(originalFile, suspectFile) {
  const errors = [];

  const originalValidation = validateImageFile(originalFile);
  if (!originalValidation.valid) {
    errors.push(`Original image: ${originalValidation.error}`);
  }

  const suspectValidation = validateImageFile(suspectFile);
  if (!suspectValidation.valid) {
    errors.push(`Suspect image: ${suspectValidation.error}`);
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate verify request (single file)
 * @param {File} file - Image file to verify
 * @returns {{valid: boolean, error?: string}} Validation result
 */
export function validateVerifyRequest(file) {
  return validateImageFile(file);
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size (e.g., "2.5 MB")
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
