import config from '../config';

/**
 * Validates a username according to configuration rules
 * @param {string} username - The username to validate
 * @returns {Object} - { isValid: boolean, errorMessage: string }
 */
export const validateUsername = (username) => {
  const rules = config.validation.username;
  
  if (!username) {
    return { isValid: false, errorMessage: rules.errorMessages.required };
  }
  
  if (username.length < rules.minLength) {
    return { isValid: false, errorMessage: rules.errorMessages.minLength };
  }
  
  if (username.length > rules.maxLength) {
    return { isValid: false, errorMessage: rules.errorMessages.maxLength };
  }
  
  if (!rules.pattern.test(username)) {
    return { isValid: false, errorMessage: rules.errorMessages.pattern };
  }
  
  return { isValid: true, errorMessage: '' };
};

/**
 * Validates a password according to configuration rules
 * @param {string} password - The password to validate
 * @returns {Object} - { isValid: boolean, errorMessage: string }
 */
export const validatePassword = (password) => {
  const rules = config.validation.password;
  
  if (!password) {
    return { isValid: false, errorMessage: rules.errorMessages.required };
  }
  
  if (password.length < rules.minLength) {
    return { isValid: false, errorMessage: rules.errorMessages.minLength };
  }
  
  if (password.length > rules.maxLength) {
    return { isValid: false, errorMessage: rules.errorMessages.maxLength };
  }
  
  if (rules.requireUppercase && !/[A-Z]/.test(password)) {
    return { isValid: false, errorMessage: rules.errorMessages.requireUppercase };
  }
  
  if (rules.requireLowercase && !/[a-z]/.test(password)) {
    return { isValid: false, errorMessage: rules.errorMessages.requireLowercase };
  }
  
  if (rules.requireNumbers && !/[0-9]/.test(password)) {
    return { isValid: false, errorMessage: rules.errorMessages.requireNumbers };
  }
  
  if (rules.requireSpecial && !new RegExp(`[${rules.specialChars.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')}]`).test(password)) {
    return { isValid: false, errorMessage: rules.errorMessages.requireSpecial };
  }
  
  return { isValid: true, errorMessage: '' };
};

/**
 * Validates a customer name according to configuration rules
 * @param {string} name - The customer name to validate
 * @returns {Object} - { isValid: boolean, errorMessage: string }
 */
export const validateCustomerName = (name) => {
  const rules = config.validation.customerName;
  
  if (!name) {
    return { isValid: false, errorMessage: rules.errorMessages.required };
  }
  
  if (name.length < rules.minLength) {
    return { isValid: false, errorMessage: rules.errorMessages.minLength };
  }
  
  if (name.length > rules.maxLength) {
    return { isValid: false, errorMessage: rules.errorMessages.maxLength };
  }
  
  if (!rules.pattern.test(name)) {
    return { isValid: false, errorMessage: rules.errorMessages.pattern };
  }
  
  return { isValid: true, errorMessage: '' };
};
