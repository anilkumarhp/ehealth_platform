// Utility functions for handling session storage

// Save entity data to session storage
export const saveEntityToSession = (entityType, entityData) => {
  try {
    sessionStorage.setItem('selectedEntityType', entityType);
    sessionStorage.setItem('selectedEntityData', JSON.stringify(entityData));
    return true;
  } catch (error) {
    console.error('Error saving entity to session storage:', error);
    return false;
  }
};

// Get entity data from session storage
export const getEntityFromSession = () => {
  try {
    const entityType = sessionStorage.getItem('selectedEntityType');
    const entityDataString = sessionStorage.getItem('selectedEntityData');
    
    if (!entityType || !entityDataString) {
      return { entityType: null, entityData: null };
    }
    
    const entityData = JSON.parse(entityDataString);
    
    // Clear session storage after retrieving data
    sessionStorage.removeItem('selectedEntityType');
    sessionStorage.removeItem('selectedEntityData');
    
    return { entityType, entityData };
  } catch (error) {
    console.error('Error getting entity from session storage:', error);
    return { entityType: null, entityData: null };
  }
};