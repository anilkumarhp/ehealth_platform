import { useState, useEffect } from 'react';
import { User, Upload, Save, X } from 'lucide-react';
import userService from '../services/userService';
import authService from '../services/authService';

const UserProfileForm = () => {
  const [activeTab, setActiveTab] = useState('personal');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [profileData, setProfileData] = useState({
    // Personal Information
    firstName: '',
    lastName: '',
    displayName: '',
    dateOfBirth: '',
    gender: '',
    bloodGroup: '',
    email: '',
    phone: '',
    emergencyContact: '',
    
    // Address Details
    street: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    addressType: 'home',
    
    // Security Settings
    mfaEnabled: false,
    
    // Insurance Information
    hasInsurance: false,
    insurances: [],
  });
  
  // Fetch user profile data when component mounts
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setIsLoading(true);
        
        // Try to get profile tabs first (new endpoint)
        try {
          const tabsData = await userService.getProfileTabs();
          
          if (tabsData && tabsData.tabs) {
            // We have the new tabs format
            const personalTab = tabsData.tabs.find(tab => tab.id === 'personal')?.fields || {};
            const addressTab = tabsData.tabs.find(tab => tab.id === 'address')?.fields || {};
            const accountTab = tabsData.tabs.find(tab => tab.id === 'account')?.fields || {};
            const insuranceTab = tabsData.tabs.find(tab => tab.id === 'insurance')?.fields || {};
            
            // Process insurance data
            let insurances = [];
            if (insuranceTab.insurance && Array.isArray(insuranceTab.insurance)) {
              insurances = insuranceTab.insurance;
            }
            
            setProfileData({
              firstName: personalTab.first_name || '',
              lastName: personalTab.last_name || '',
              displayName: personalTab.display_name || '',
              dateOfBirth: personalTab.date_of_birth || '',
              gender: personalTab.gender || '',
              bloodGroup: personalTab.blood_group || '',
              email: accountTab.email || '',
              phone: accountTab.phone || '',
              emergencyContact: personalTab.emergency_contact || '',
              
              street: addressTab.street || '',
              city: addressTab.city || '',
              state: addressTab.state || '',
              zipCode: addressTab.zip_code || '',
              country: addressTab.country || '',
              addressType: addressTab.address_type || 'home',
              
              mfaEnabled: accountTab.enable_mfa || false,
              
              hasInsurance: insuranceTab.has_insurance || insurances.length > 0,
              insurances: insurances,
              showInsuranceForm: false,
              editingInsurance: null,
              tempInsurance: null
            });
            
            // Set photo preview if available
            if (tabsData.profile_photo_url) {
              setPhotoPreview(tabsData.profile_photo_url);
            }
            
            console.log('Profile photo URL from tabs:', tabsData.profile_photo_url);
            
            setIsLoading(false);
            return;
          }
        } catch (tabsError) {
          console.warn('Could not fetch profile tabs, falling back to legacy endpoint:', tabsError);
        }
        
        // Fallback to the old endpoint
        const userData = await userService.getUserProfile();
        
        // Map API data to form fields
        const personalInfo = userData.personal_info || {};
        const address = personalInfo.address || {};
        
        // Process insurance data
        let insurances = [];
        if (userData.insurance_info && Array.isArray(userData.insurance_info)) {
          insurances = userData.insurance_info;
        } else if (userData.patient_profile?.insurances && Array.isArray(userData.patient_profile.insurances)) {
          insurances = userData.patient_profile.insurances;
        }
        
        setProfileData({
          firstName: personalInfo.first_name || '',
          lastName: personalInfo.last_name || '',
          displayName: personalInfo.display_name || '',
          dateOfBirth: personalInfo.date_of_birth || '',
          gender: personalInfo.gender || '',
          bloodGroup: personalInfo.blood_group || '',
          email: userData.email || '',
          phone: userData.primary_phone || '',
          emergencyContact: personalInfo.emergency_contact || '',
          
          street: address.street || '',
          city: address.city || '',
          state: address.state || '',
          zipCode: address.zip_code || '',
          country: address.country || '',
          addressType: address.address_type || 'home',
          
          mfaEnabled: userData.mfa_enabled || false,
          
          hasInsurance: userData.has_insurance || insurances.length > 0,
          insurances: insurances,
          showInsuranceForm: false,
          editingInsurance: null,
          tempInsurance: null
        });
        
        // Set photo preview if available
        if (userData.profile_photo_url) {
          setPhotoPreview(userData.profile_photo_url);
        } else if (userData.profile_data?.photo) {
          setPhotoPreview(userData.profile_data.photo);
        }
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching user profile:', err);
        setError('Failed to load user profile. Please try again later.');
        setIsLoading(false);
      }
    };
    
    fetchUserProfile();
  }, []);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Revoke previous preview URL to avoid memory leaks
      if (photoPreview && photoPreview.startsWith('blob:')) {
        URL.revokeObjectURL(photoPreview);
      }
      
      setPhotoFile(file);
      setPhotoPreview(URL.createObjectURL(file));
      
      // Upload the photo immediately for better user experience
      uploadPhoto(file);
    }
  };
  
  const uploadPhoto = async (file) => {
    try {
      setIsSaving(true);
      
      // Convert file to base64
      const base64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      
      // Use base64 upload method
      const result = await userService.updateProfilePhotoBase64(base64);
      console.log('Photo uploaded successfully:', result);
      
      // If the server returns a URL, use it instead of the blob URL
      if (result && result.photo_url) {
        setPhotoPreview(result.photo_url);
        
        // Update the stored user data with the new photo URL
        try {
          const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
          localStorage.setItem('user', JSON.stringify({
            ...storedUser,
            photoUrl: result.photo_url
          }));
        } catch (e) {
          console.error('Error updating stored user data:', e);
        }
        
        // Refresh profile data to get updated photo URL
        try {
          const updatedProfile = await userService.getProfileTabs();
          if (updatedProfile && updatedProfile.profile_photo_url) {
            setPhotoPreview(updatedProfile.profile_photo_url);
          }
        } catch (e) {
          console.error('Error refreshing profile data:', e);
        }
        
        setSuccessMessage('Profile photo updated successfully!');
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    } catch (err) {
      console.error('Error uploading photo:', err);
      setError('Failed to upload profile photo. Please try again.');
      setTimeout(() => setError(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      // Prepare insurance data
      const insuranceData = profileData.insurances || [];
      
      // First update profile data
      await userService.updateUserProfile({
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        display_name: profileData.displayName,
        date_of_birth: profileData.dateOfBirth,
        gender: profileData.gender,
        blood_group: profileData.bloodGroup,
        emergency_contact: profileData.emergencyContact,
        phone: profileData.phone,
        
        street: profileData.street,
        city: profileData.city,
        state: profileData.state,
        zip_code: profileData.zipCode,
        country: profileData.country,
        address_type: profileData.addressType,
        
        enable_mfa: profileData.mfaEnabled,
        
        has_insurance: insuranceData.length > 0,
        insurance: insuranceData
      });
      
      // Then upload photo if changed
      if (photoFile) {
        await userService.updateProfilePhoto(photoFile);
      }
      
      setSuccessMessage('Profile updated successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-800">Profile Information</h2>
        <p className="text-sm text-gray-500">Update your personal details and preferences</p>
      </div>
      
      {/* Tabs */}
      <div className="flex border-b overflow-x-auto">
        <button
          className={`px-6 py-3 text-sm font-medium ${activeTab === 'personal' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('personal')}
        >
          Personal Details
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium ${activeTab === 'address' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('address')}
        >
          Contact & Address
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium ${activeTab === 'insurance' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('insurance')}
        >
          Insurance Details
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium ${activeTab === 'security' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('security')}
        >
          Security & MFA
        </button>
      </div>
      
      {/* Error and Success Messages */}
      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-center">
          <X className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}
      
      {successMessage && (
        <div className="mx-6 mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md flex items-center">
          <Save className="w-5 h-5 mr-2" />
          {successMessage}
        </div>
      )}
      
      {/* Personal Information Tab */}
      {activeTab === 'personal' && (
        <div className="p-6">
          {/* Profile Photo */}
          <div className="flex flex-col items-center mb-6">
            <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-100 mb-4 flex items-center justify-center border">
              {photoPreview ? (
                <img src={photoPreview} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <User className="w-16 h-16 text-gray-400" />
              )}
            </div>
            <label className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-md cursor-pointer hover:bg-blue-100 transition-colors">
              <Upload className="w-4 h-4 mr-2" />
              <span className="text-sm font-medium">Upload Photo</span>
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handlePhotoChange}
              />
            </label>
          </div>
          
          {/* Form Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name
              </label>
              <input
                type="text"
                name="firstName"
                value={profileData.firstName}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Name
              </label>
              <input
                type="text"
                name="lastName"
                value={profileData.lastName}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Display Name
              </label>
              <input
                type="text"
                name="displayName"
                value={profileData.displayName}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="How you want to be addressed"
              />
              <p className="mt-1 text-xs text-gray-500">Leave blank to use your full name</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date of Birth
              </label>
              <input
                type="date"
                name="dateOfBirth"
                value={profileData.dateOfBirth}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Gender
              </label>
              <select
                name="gender"
                value={profileData.gender}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Blood Group
              </label>
              <select
                name="bloodGroup"
                value={profileData.bloodGroup}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select Blood Group</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={profileData.email}
                disabled
                className="w-full px-3 py-2 border border-gray-200 bg-gray-50 rounded-md text-gray-500"
              />
              <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={profileData.phone}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Emergency Contact
              </label>
              <input
                type="tel"
                name="emergencyContact"
                value={profileData.emergencyContact}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      )}
      
      {/* Address Tab */}
      {activeTab === 'address' && (
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Street Address
              </label>
              <input
                type="text"
                name="street"
                value={profileData.street}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                name="city"
                value={profileData.city}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State/Province
              </label>
              <input
                type="text"
                name="state"
                value={profileData.state}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ZIP/Postal Code
              </label>
              <input
                type="text"
                name="zipCode"
                value={profileData.zipCode}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <input
                type="text"
                name="country"
                value={profileData.country}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address Type
              </label>
              <select
                name="addressType"
                value={profileData.addressType}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="home">Home</option>
                <option value="work">Work</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
        </div>
      )}
      
      {/* Insurance Information Tab */}
      {activeTab === 'insurance' && (
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-medium text-gray-800">Insurance Information</h3>
              <p className="text-sm text-gray-500">Manage your health insurance details</p>
            </div>
            <button
              onClick={() => {
                setProfileData(prev => ({
                  ...prev,
                  editingInsurance: null,
                  showInsuranceForm: true,
                  tempInsurance: {
                    provider_name: '',
                    policy_number: '',
                    scheme_name: '',
                    insurance_category: '',
                    group_number: '',
                    plan_type: '',
                    effective_date: '',
                    expiration_date: '',
                    copay_amount: '',
                    deductible_amount: '',
                    policy_holder_name: '',
                    relationship_to_policy_holder: ''
                  }
                }));
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center text-sm"
            >
              + Add Insurance
            </button>
          </div>
          
          {/* List of Insurance Policies */}
          {profileData.insurances && profileData.insurances.length > 0 ? (
            <div className="space-y-4 mb-6">
              {profileData.insurances.map((insurance, index) => (
                <div key={index} className="border rounded-md p-4 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-medium text-gray-800">{insurance.provider_name || 'Insurance Policy'}</h4>
                      <p className="text-sm text-gray-500">Policy #: {insurance.policy_number}</p>
                    </div>
                    <button
                      onClick={() => {
                        setProfileData(prev => ({
                          ...prev,
                          editingInsurance: index,
                          showInsuranceForm: true,
                          tempInsurance: { ...insurance }
                        }));
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Edit
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {insurance.scheme_name && (
                      <div>
                        <span className="text-gray-500">Scheme:</span> {insurance.scheme_name}
                      </div>
                    )}
                    {insurance.insurance_category && (
                      <div>
                        <span className="text-gray-500">Category:</span> {insurance.insurance_category}
                      </div>
                    )}
                    {insurance.group_number && (
                      <div>
                        <span className="text-gray-500">Group #:</span> {insurance.group_number}
                      </div>
                    )}
                    {insurance.plan_type && (
                      <div>
                        <span className="text-gray-500">Plan Type:</span> {insurance.plan_type}
                      </div>
                    )}
                    {insurance.effective_date && (
                      <div>
                        <span className="text-gray-500">Effective:</span> {insurance.effective_date}
                      </div>
                    )}
                    {insurance.expiration_date && (
                      <div>
                        <span className="text-gray-500">Expires:</span> {insurance.expiration_date}
                      </div>
                    )}
                    {insurance.copay_amount && (
                      <div>
                        <span className="text-gray-500">Copay:</span> {insurance.copay_amount}
                      </div>
                    )}
                    {insurance.deductible_amount && (
                      <div>
                        <span className="text-gray-500">Deductible:</span> {insurance.deductible_amount}
                      </div>
                    )}
                    {insurance.policy_holder_name && (
                      <div>
                        <span className="text-gray-500">Policy Holder:</span> {insurance.policy_holder_name}
                      </div>
                    )}
                    {insurance.relationship_to_policy_holder && (
                      <div>
                        <span className="text-gray-500">Relationship:</span> {insurance.relationship_to_policy_holder}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 border rounded-md">
              <p>No insurance information added</p>
              <p className="text-sm mt-2">Click "Add Insurance" to add your insurance details</p>
            </div>
          )}
          
          {/* Insurance Form */}
          {profileData.showInsuranceForm && (
            <div className="border rounded-md p-4 bg-gray-50 mt-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-md font-medium text-gray-800">
                  {profileData.editingInsurance !== null ? 'Edit Insurance' : 'Add New Insurance'}
                </h3>
                <button
                  onClick={() => setProfileData(prev => ({ ...prev, showInsuranceForm: false, editingInsurance: null }))}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Provider Name*
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.provider_name || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, provider_name: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Policy Number*
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.policy_number || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, policy_number: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scheme Name
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.scheme_name || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, scheme_name: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Insurance Category
                  </label>
                  <select
                    value={profileData.tempInsurance?.insurance_category || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, insurance_category: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="">Select Category</option>
                    <option value="private">Private</option>
                    <option value="government">Government</option>
                    <option value="employer">Employer</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Group Number
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.group_number || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, group_number: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Plan Type
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.plan_type || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, plan_type: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Effective Date
                  </label>
                  <input
                    type="date"
                    value={profileData.tempInsurance?.effective_date || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, effective_date: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expiration Date
                  </label>
                  <input
                    type="date"
                    value={profileData.tempInsurance?.expiration_date || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, expiration_date: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Copay Amount
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.copay_amount || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, copay_amount: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder="e.g. $20"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Deductible Amount
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.deductible_amount || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, deductible_amount: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder="e.g. $500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Policy Holder Name
                  </label>
                  <input
                    type="text"
                    value={profileData.tempInsurance?.policy_holder_name || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, policy_holder_name: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Relationship to Policy Holder
                  </label>
                  <select
                    value={profileData.tempInsurance?.relationship_to_policy_holder || ''}
                    onChange={(e) => setProfileData(prev => ({
                      ...prev,
                      tempInsurance: { ...prev.tempInsurance, relationship_to_policy_holder: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="">Select Relationship</option>
                    <option value="self">Self</option>
                    <option value="spouse">Spouse</option>
                    <option value="child">Child</option>
                    <option value="parent">Parent</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-4 flex justify-end space-x-2">
                <button
                  onClick={() => setProfileData(prev => ({ ...prev, showInsuranceForm: false, editingInsurance: null }))}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    // Validate required fields
                    if (!profileData.tempInsurance?.provider_name || !profileData.tempInsurance?.policy_number) {
                      setError('Provider name and policy number are required.');
                      return;
                    }
                    
                    // Update or add insurance
                    const updatedInsurances = [...(profileData.insurances || [])];
                    if (profileData.editingInsurance !== null) {
                      updatedInsurances[profileData.editingInsurance] = profileData.tempInsurance;
                    } else {
                      updatedInsurances.push(profileData.tempInsurance);
                    }
                    
                    setProfileData(prev => ({
                      ...prev,
                      insurances: updatedInsurances,
                      showInsuranceForm: false,
                      editingInsurance: null,
                      hasInsurance: true
                    }));
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  {profileData.editingInsurance !== null ? 'Update' : 'Add'} Insurance
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Security & MFA Tab */}
      {activeTab === 'security' && (
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">Multi-Factor Authentication (MFA)</h3>
            <p className="text-sm text-gray-500 mb-4">
              Enhance your account security by enabling multi-factor authentication.
            </p>
            
            <div className="flex items-center mb-4">
              <div className={`w-4 h-4 rounded-full mr-2 ${profileData.mfaEnabled ? 'bg-green-500' : 'bg-gray-300'}`}></div>
              <span className="font-medium">
                MFA is currently {profileData.mfaEnabled ? 'enabled' : 'disabled'}
              </span>
            </div>
            
            <div className="flex space-x-4">
              {profileData.mfaEnabled ? (
                <button
                  onClick={() => {
                    if (window.confirm('Are you sure you want to disable MFA?')) {
                      setProfileData(prev => ({ ...prev, mfaEnabled: false }));
                    }
                  }}
                  className="px-4 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50"
                >
                  Disable MFA
                </button>
              ) : (
                <button
                  onClick={() => setProfileData(prev => ({ ...prev, showMfaSetup: true }))}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Enable MFA
                </button>
              )}
            </div>
          </div>
          
          {/* MFA Setup Section */}
          {!profileData.mfaEnabled && profileData.showMfaSetup && (
            <div className="border rounded-md p-4 bg-gray-50 mt-6">
              <h4 className="font-medium text-gray-800 mb-4">MFA Setup</h4>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  1. Scan this QR code with your authenticator app
                </p>
                <div className="bg-white p-4 inline-block rounded border">
                  <div className="w-48 h-48 bg-gray-200 flex items-center justify-center">
                    <span className="text-gray-500 text-sm">QR Code Placeholder</span>
                  </div>
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  2. Enter the verification code from your authenticator app
                </p>
                <input
                  type="text"
                  placeholder="Enter 6-digit code"
                  className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  maxLength={6}
                  value={profileData.mfaCode || ''}
                  onChange={(e) => setProfileData(prev => ({ ...prev, mfaCode: e.target.value.replace(/[^0-9]/g, '') }))}
                />
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => setProfileData(prev => ({ ...prev, showMfaSetup: false }))}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    setProfileData(prev => ({ ...prev, mfaEnabled: true, showMfaSetup: false }));
                    setSuccessMessage('MFA has been successfully enabled!');
                    setTimeout(() => setSuccessMessage(null), 3000);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  disabled={!profileData.mfaCode || profileData.mfaCode.length !== 6}
                >
                  Verify & Enable
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Footer with Save Button */}
      <div className="px-6 py-4 bg-gray-50 border-t flex justify-end">
        <button
          onClick={handleSaveProfile}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default UserProfileForm;