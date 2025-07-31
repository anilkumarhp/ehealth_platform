import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import MFASetupTab from '../components/MFASetupTab';
import apiUtils from '../utils/apiUtils';
import '../index.css'; // Make sure CSS is imported

const privateInsuranceTypes = [
  'Individual Health Insurance',
  'Family Floater Health Insurance',
  'Senior Citizen Health Insurance',
  'Critical Illness Insurance',
  'Top-up Plans',
  'Super Top-up Plans',
  'Disease-Specific Plans',
  'Maternity Health Insurance',
  'Personal Accident Insurance'
];

const governmentInsuranceTypes = [
  'Ayushman Bharat - PM-JAY',
  'Central Government Health Scheme (CGHS)',
  'Employees State Insurance Scheme (ESIC)',
  'Aam Aadmi Bima Yojana (AABY)',
  'Aarogyasri (Telangana/Andhra Pradesh)',
  'Mukhyamantri Chiranjeevi Swasthya Bima Yojana (Rajasthan)',
  'Mahatma Jyotiba Phule Jan Arogya Yojana (Maharashtra)',
  'Biju Swasthya Kalyan Yojana (Odisha)'
];

// Minimal CSS styles
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'Inter, sans-serif'
  },
  navbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    borderBottom: '1px solid #e5e7eb'
  },
  logoContainer: {
    display: 'flex',
    alignItems: 'center'
  },
  logoIcon: {
    width: '40px',
    height: '40px',
    backgroundColor: '#3b82f6',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontWeight: 'bold',
    marginRight: '10px'
  },
  logoText: {
    fontWeight: 'bold',
    fontSize: '1.25rem'
  },
  loginLink: {
    textDecoration: 'none',
    color: '#3b82f6',
    fontWeight: '500'
  },
  mainContent: {
    width: '80%',
    margin: '40px auto',
    padding: '30px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
    flex: 1
  },
  tabContainer: {
    display: 'flex',
    borderBottom: '1px solid #e5e7eb',
    marginBottom: '24px',
  },
  tab: {
    padding: '12px 24px',
    cursor: 'pointer',
    border: 'none',
    background: 'none',
    fontSize: '16px',
    position: 'relative',
    transition: 'all 0.2s',
  },
  activeTab: {
    borderBottom: '2px solid #3b82f6',
    color: '#3b82f6',
    fontWeight: '600',
  },
  formSection: {
    padding: '32px',
    backgroundColor: '#fff',
    borderRadius: '10px',
    marginBottom: '32px',
    border: '1px solid #e5e7eb',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
  },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '24px 32px',
    marginBottom: '32px',
  },
  formField: {
    marginBottom: '28px',
    position: 'relative',
  },
  label: {
    display: 'block',
    marginBottom: '10px',
    fontWeight: '500',
    color: '#374151',
    fontSize: '15px',
  },
  input: {
    width: '100%',
    padding: '14px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    boxSizing: 'border-box',
    boxShadow: 'inset 0 1px 2px rgba(0, 0, 0, 0.05)',
    fontSize: '15px',
    transition: 'all 0.2s',
    outline: 'none',
  },
  select: {
    width: '100%',
    padding: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    boxSizing: 'border-box',
    boxShadow: 'inset 0 1px 2px rgba(0, 0, 0, 0.05)',
    fontSize: '16px',
    appearance: 'none',
    backgroundImage: 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\' fill=\'%236b7280\' viewBox=\'0 0 16 16\'%3E%3Cpath d=\'M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z\' /%3E%3C/svg%3E")',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px center',
    paddingRight: '40px',
  },
  button: {
    padding: '12px 24px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '500',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    transition: 'all 0.2s',
    fontSize: '16px',
  },
  primaryButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
  },
  secondaryButton: {
    backgroundColor: '#9ca3af',
    color: 'white',
    marginRight: '12px',
  },
  dangerButton: {
    backgroundColor: '#ef4444',
    color: 'white',
    marginRight: '12px',
  },
  successButton: {
    backgroundColor: '#10b981',
    color: 'white',
  },
  buttonContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '24px',
  },
  errorBox: {
    backgroundColor: '#fee2e2',
    border: '1px solid #f87171',
    color: '#b91c1c',
    padding: '16px',
    borderRadius: '6px',
    marginBottom: '20px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
  },
  warningBox: {
    backgroundColor: '#fef3c7',
    border: '1px solid #fbbf24',
    color: '#92400e',
    padding: '16px',
    borderRadius: '6px',
    marginBottom: '20px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
  },
  insuranceCard: {
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    padding: '16px',
    marginBottom: '16px',
    boxShadow: '0 2px 6px rgba(0, 0, 0, 0.08)',
    transition: 'all 0.2s',
  },
  insuranceForm: {
    backgroundColor: '#f9fafb',
    padding: '24px',
    borderRadius: '8px',
    marginBottom: '24px',
    border: '1px solid #e5e7eb',
    boxShadow: '0 2px 6px rgba(0, 0, 0, 0.08)',
  },
  link: {
    color: '#3b82f6',
    textDecoration: 'none',
    fontWeight: '500',
  },
  heading: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '24px',
    color: '#111827',
  },
  subheading: {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '24px',
    color: '#374151',
  },
  progressBar: {
    height: '4px',
    backgroundColor: '#e5e7eb',
    borderRadius: '2px',
    marginBottom: '24px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3b82f6',
    transition: 'width 0.3s ease',
  },
  fileInput: {
    display: 'none',
  },
  fileLabel: {
    display: 'inline-block',
    padding: '10px 16px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    cursor: 'pointer',
    color: '#374151',
    fontWeight: '500',
    transition: 'all 0.2s',
  },
  fileInfo: {
    marginTop: '8px',
    fontSize: '14px',
    color: '#6b7280',
  },
  photoUploadContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginBottom: '32px',
    width: '100%',
  },
  photoPreviewContainer: {
    width: '150px',
    height: '150px',
    borderRadius: '50%',
    border: '2px dashed #d1d5db',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '16px',
    overflow: 'hidden',
    backgroundColor: '#f9fafb',
  },
  photoPreview: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  photoPlaceholder: {
    color: '#9ca3af',
    fontSize: '14px',
    textAlign: 'center',
    padding: '0 16px',
  },
  photoUploadButton: {
    display: 'inline-block',
    padding: '10px 20px',
    backgroundColor: '#3b82f6',
    color: 'white',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s',
    border: 'none',
    textAlign: 'center',
  },
  infoText: {
    fontSize: '14px',
    color: '#6b7280',
    marginTop: '4px',
  },
  requiredField: {
    color: '#ef4444',
    marginLeft: '4px',
  },
  invalidInput: {
    border: '1px solid #ef4444',
    backgroundColor: '#fef2f2',
  },
  validInput: {
    border: '1px solid #10b981',
    backgroundColor: '#f0fdf4',
  },
  passwordHints: {
    position: 'absolute',
    top: 'calc(100% + 5px)',
    right: '0',
    width: '250px',
    padding: '10px 12px',
    backgroundColor: 'white',
    borderRadius: '6px',
    fontSize: '13px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    border: '1px solid #e5e7eb',
    zIndex: 10,
    animation: 'fadeIn 0.2s ease-in-out',
  },
  passwordHint: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
    fontSize: '13px',
  },
  validHint: {
    color: '#10b981',
    fontWeight: '500',
  },
  invalidHint: {
    color: '#6b7280',
  },
  passwordHintIcon: {
    marginRight: '8px',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '18px',
    height: '18px',
  },
  passwordFieldContainer: {
    position: 'relative',
  },
  fieldError: {
    color: '#ef4444',
    fontSize: '13px',
    marginTop: '6px',
    fontWeight: '500',
  },
};

const PatientRegistrationPage = () => {
  const [activeTab, setActiveTab] = useState('basic');
  const [mfaSecret, setMfaSecret] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [otp, setOtp] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [apiAvailable, setApiAvailable] = useState(true);
  const [validationErrors, setValidationErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [showPasswordHints, setShowPasswordHints] = useState(false);
  const [passwordCriteria, setPasswordCriteria] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  });
  const [hasFamilyMembers, setHasFamilyMembers] = useState(false);
  const [familyMembers, setFamilyMembers] = useState([]);
  const [currentFamilyMember, setCurrentFamilyMember] = useState({
    fullName: '',
    relation: '',
    gender: '',
    contactNumber: '',
    aadhaarId: ''
  });
  const [editingFamilyMember, setEditingFamilyMember] = useState(null);
  const [formData, setFormData] = useState({
    // Basic Details
    firstName: '',
    lastName: '',
    displayName: '',
    dateOfBirth: '',
    gender: '',
    bloodGroup: '',
    customBloodGroup: '',
    email: '',
    phone: '',
    emergencyContact: '',
    password: '',
    confirmPassword: '',
    aadharId: '',
    photo: null,
    photoPreview: null,
    // Address Details
    street: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    addressType: 'home',
    // Insurance Details
    hasInsurance: false,
    insuranceList: [],
    // MFA Details
    enableMfa: false
  });
  
  const [currentInsurance, setCurrentInsurance] = useState({
    insuranceCategory: '',
    insuranceType: '',
    customType: '',
    providerName: '',
    policyNumber: '',
    groupNumber: '',
    planType: '',
    effectiveDate: '',
    expirationDate: '',
    copayAmount: '',
    deductibleAmount: '',
    policyHolderName: '',
    relationshipToPolicyHolder: 'self',
    insuranceFiles: []
  });
  
  const [editingInsurance, setEditingInsurance] = useState(null);
  
  const navigate = useNavigate();
  
  // Check API availability when component mounts
  useEffect(() => {
    const checkApi = async () => {
      const isAvailable = await apiUtils.checkApiAvailability();
      setApiAvailable(isAvailable);
      if (!isAvailable) {
        setError('Unable to connect to the server. Please ensure the backend service is running.');
      }
    };
    
    checkApi();
    
    // Cleanup function to revoke object URLs when component unmounts
    return () => {
      if (formData.photoPreview) {
        URL.revokeObjectURL(formData.photoPreview);
      }
    };
  }, []);

  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'firstName':
      case 'lastName':
        if (!value.trim()) error = 'This field is required';
        break;
      case 'email':
        if (!value.trim()) {
          error = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          error = 'Please enter a valid email address';
        }
        break;
      case 'phone':
        if (!value.trim()) {
          error = 'Phone number is required';
        } else if (!/^\d{10}$/.test(value.replace(/[\s-]/g, ''))) {
          error = 'Please enter a valid 10-digit phone number';
        }
        break;
      case 'password':
        if (!value) {
          error = 'Password is required';
        } else if (value.length < 12) {
          error = 'Password must be at least 12 characters';
        }
        break;
      case 'confirmPassword':
        if (value !== formData.password) {
          error = 'Passwords do not match';
        }
        break;
      default:
        break;
    }
    
    return error;
  };
  
  const checkPasswordCriteria = (password) => {
    const criteria = {
      length: password.length >= 12,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
    
    setPasswordCriteria(criteria);
    
    // Check if all criteria are met
    const allCriteriaMet = Object.values(criteria).every(Boolean);
    if (allCriteriaMet) {
      // Hide hints after a short delay
      setTimeout(() => setShowPasswordHints(false), 500);
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));
    
    // Mark field as touched
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    // Validate the field
    const error = validateField(name, newValue);
    setValidationErrors(prev => ({
      ...prev,
      [name]: error
    }));
    
    // Check password criteria if password field
    if (name === 'password') {
      if (value) {
        setShowPasswordHints(true);
        checkPasswordCriteria(value);
      } else {
        setShowPasswordHints(false);
      }
    }
    
    // Validate confirm password when password changes
    if (name === 'password' && formData.confirmPassword) {
      const confirmError = formData.confirmPassword !== value ? 'Passwords do not match' : '';
      setValidationErrors(prev => ({
        ...prev,
        confirmPassword: confirmError
      }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Revoke the previous object URL to avoid memory leaks
      if (formData.photoPreview) {
        URL.revokeObjectURL(formData.photoPreview);
      }
      
      const photoURL = URL.createObjectURL(file);
      setFormData(prev => ({
        ...prev,
        photo: file,
        photoPreview: photoURL
      }));
    }
  };

  const handleInsuranceInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentInsurance(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleInsuranceFileChange = (e) => {
    const files = Array.from(e.target.files);
    setCurrentInsurance(prev => ({
      ...prev,
      insuranceFiles: [...prev.insuranceFiles, ...files]
    }));
  };

  const addInsurance = () => {
    if ((currentInsurance.insuranceCategory === 'government' || currentInsurance.providerName) && currentInsurance.policyNumber) {
      const insuranceData = {
        ...currentInsurance,
        id: editingInsurance ? editingInsurance.id : Date.now(),
        displayName: currentInsurance.insuranceType === 'other' ? currentInsurance.customType : currentInsurance.insuranceType
      };
      
      if (editingInsurance) {
        setFormData(prev => ({
          ...prev,
          insuranceList: prev.insuranceList.map(ins => 
            ins.id === editingInsurance.id ? insuranceData : ins
          )
        }));
        setEditingInsurance(null);
      } else {
        setFormData(prev => ({
          ...prev,
          insuranceList: [...prev.insuranceList, insuranceData]
        }));
      }
      
      setCurrentInsurance({
        insuranceCategory: '',
        insuranceType: '',
        customType: '',
        providerName: '',
        policyNumber: '',
        groupNumber: '',
        planType: '',
        effectiveDate: '',
        expirationDate: '',
        copayAmount: '',
        deductibleAmount: '',
        policyHolderName: '',
        relationshipToPolicyHolder: 'self',
        insuranceFiles: []
      });
    }
  };
  
  const editInsurance = (insurance) => {
    setCurrentInsurance(insurance);
    setEditingInsurance(insurance);
  };

  const removeInsurance = (id) => {
    setFormData(prev => ({
      ...prev,
      insuranceList: prev.insuranceList.filter(ins => ins.id !== id)
    }));
  };

  const removeInsuranceFile = (index) => {
    setCurrentInsurance(prev => ({
      ...prev,
      insuranceFiles: prev.insuranceFiles.filter((_, i) => i !== index)
    }));
  };

  const handleNext = () => {
    if (activeTab === 'basic') {
      setActiveTab('address');
    } else if (activeTab === 'address') {
      setActiveTab('insurance');
    } else if (activeTab === 'insurance') {
      setActiveTab('family');
    } else if (activeTab === 'family') {
      setActiveTab('mfa');
    }
  };

  const handlePrevious = () => {
    if (activeTab === 'mfa') {
      setActiveTab('family');
    } else if (activeTab === 'family') {
      setActiveTab('insurance');
    } else if (activeTab === 'insurance') {
      setActiveTab('address');
    } else if (activeTab === 'address') {
      setActiveTab('basic');
    }
  };

  const handleFamilyMemberInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentFamilyMember(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addFamilyMember = () => {
    if (currentFamilyMember.fullName && currentFamilyMember.relation) {
      const memberData = {
        ...currentFamilyMember,
        id: editingFamilyMember ? editingFamilyMember.id : Date.now()
      };
      
      if (editingFamilyMember) {
        setFamilyMembers(prev => prev.map(member => 
          member.id === editingFamilyMember.id ? memberData : member
        ));
        setEditingFamilyMember(null);
      } else {
        setFamilyMembers(prev => [...prev, memberData]);
      }
      
      setCurrentFamilyMember({
        fullName: '',
        relation: '',
        gender: '',
        contactNumber: '',
        aadhaarId: ''
      });
    }
  };

  const editFamilyMember = (member) => {
    setCurrentFamilyMember(member);
    setEditingFamilyMember(member);
  };

  const removeFamilyMember = (id) => {
    setFamilyMembers(prev => prev.filter(member => member.id !== id));
  };
  
  const validateForm = () => {
    const requiredFields = ['firstName', 'lastName', 'email', 'phone', 'password', 'confirmPassword'];
    const newErrors = {};
    let isValid = true;
    
    // Mark all required fields as touched
    const newTouched = { ...touched };
    requiredFields.forEach(field => {
      newTouched[field] = true;
    });
    setTouched(newTouched);
    
    // Validate each required field
    requiredFields.forEach(field => {
      const error = validateField(field, formData[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    });
    
    // Check if password meets all criteria
    const allCriteriaMet = Object.values(passwordCriteria).every(Boolean);
    if (!newErrors.password && !allCriteriaMet) {
      newErrors.password = 'Password does not meet all requirements';
      isValid = false;
    }
    
    setValidationErrors(newErrors);
    return isValid;
  };
  
  const handleSave = async () => {
    // Validate all form fields
    if (!validateForm()) {
      setError('Please correct the errors in the form');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Prepare insurance data for API
      const insuranceData = formData.insuranceList.map(insurance => ({
        category: insurance.insuranceCategory,
        type: insurance.insuranceType === 'other' ? insurance.customType : insurance.insuranceType,
        provider_name: insurance.providerName,
        policy_number: insurance.policyNumber,
        group_number: insurance.groupNumber,
        plan_type: insurance.planType,
        effective_date: insurance.effectiveDate,
        expiration_date: insurance.expirationDate,
        copay_amount: insurance.copayAmount,
        deductible_amount: insurance.deductibleAmount,
        policy_holder_name: insurance.policyHolderName,
        relationship_to_policy_holder: insurance.relationshipToPolicyHolder
      }));
      
      // Prepare user data for API - match the backend model field names
      const userData = {
        // Required fields
        email: formData.email,
        password: formData.password,
        phone: formData.phone,  // Using 'phone' instead of 'primary_phone'
        primary_phone: formData.phone,  // Also include primary_phone for backward compatibility
        
        // Personal information
        first_name: formData.firstName,
        last_name: formData.lastName,
        display_name: formData.displayName || `${formData.firstName} ${formData.lastName}`,
        date_of_birth: formData.dateOfBirth || null,
        gender: formData.gender || null,
        blood_group: formData.bloodGroup === 'other' ? formData.customBloodGroup : (formData.bloodGroup || null),
        emergency_contact: formData.emergencyContact || null,
        aadhar_id: formData.aadharId || null,
        
        // Address information
        address: formData.street ? {
          street: formData.street,
          city: formData.city || '',
          state: formData.state || '',
          zip_code: formData.zipCode || '',
          country: formData.country || '',
          address_type: formData.addressType || 'home'
        } : null,
        
        // Insurance information
        insurance: formData.hasInsurance ? insuranceData : [],
        
        // MFA settings
        enable_mfa: formData.enableMfa || false,
        
        // Organization information - always set to "Patients" for patient registration
        organization_name: "Patients",
        
        // Add personal_info for backward compatibility
        personal_info: {
          first_name: formData.firstName,
          last_name: formData.lastName,
          display_name: formData.displayName || `${formData.firstName} ${formData.lastName}`,
          date_of_birth: formData.dateOfBirth || null,
          gender: formData.gender || null,
          emergency_contact: formData.emergencyContact || null
        }
      };
      
      // We don't send the photo directly in the registration request anymore
      // It will be uploaded separately after registration if needed
      
      // Send registration request with JSON data directly
      const response = formData.enableMfa 
        ? await authService.registerWithMfa(userData)
        : await authService.register(userData);
      
      if (response) {
        // If there's a photo, upload it separately after successful registration
        if (formData.photo) {
          try {
            // We need to be logged in to upload files, so this will only work if the registration
            // process automatically logs the user in (which it should based on the token handling)
            const uploadResponse = await authService.uploadFile(formData.photo, 'profile_photo');
            console.log('Photo upload successful:', uploadResponse);
            
            // In a real app, you might want to update the user profile with the photo URL
            // This would require an additional API call to update the user profile
          } catch (uploadError) {
            console.error('Error uploading profile photo:', uploadError);
            // Continue even if photo upload fails
          }
        }
        
        if (formData.enableMfa && response.mfa_setup) {
          // If MFA is enabled, store the secret and QR code
          setMfaSecret(response.mfa_setup.secret);
          setQrCode(response.mfa_setup.qr_code);
          // Navigate to MFA setup page
          navigate('/mfa-setup', { 
            state: { 
              mfaSecret: response.mfa_setup.secret, 
              qrCode: response.mfa_setup.qr_code,
              userId: response.user_id,
              email: response.email
            } 
          });
        } else {
          // Navigate to dashboard directly since we now have tokens
          navigate('/dashboard', { state: { message: 'Registration successful!' } });
        }
      } else {
        setError(response.message || 'Registration failed. Please try again.');
      }
    } catch (err) {
      console.error('Registration error:', err);
      
      // Extract detailed error message from response if available
      let errorMessage = 'An error occurred during registration. Please try again.';
      
      if (err.response && err.response.data) {
        if (err.response.data.detail) {
          if (typeof err.response.data.detail === 'string') {
            errorMessage = err.response.data.detail;
          } else if (Array.isArray(err.response.data.detail)) {
            // Handle validation errors array format
            errorMessage = err.response.data.detail.map(error => 
              `${error.loc.join('.')} - ${error.msg}`
            ).join('\n');
          }
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Helper function to convert File to base64 string
  const convertFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.split(',')[1]); // Remove the data:image/jpeg;base64, part
      reader.onerror = (error) => reject(error);
    });
  };
  
  // Calculate progress percentage based on active tab
  const getProgressPercentage = () => {
    switch (activeTab) {
      case 'basic':
        return 20;
      case 'address':
        return 40;
      case 'insurance':
        return 60;
      case 'family':
        return 80;
      case 'mfa':
        return 100;
      default:
        return 0;
    }
  };
  
  return (
    <div style={styles.container}>
      {/* Navbar - Identical to LandingPage */}
      <nav style={styles.navbar}>
        <div style={styles.logoContainer}>
          <div style={styles.logoIcon}>E</div>
          <span style={styles.logoText}>eHealth Platform</span>
        </div>
        <Link to="/login" style={styles.loginLink}>
          Login
        </Link>
      </nav>
      
      {/* Main Content */}
      <div style={styles.mainContent}>
        <h1 style={styles.heading}>Patient Registration</h1>
        
        {/* Progress bar */}
        <div style={styles.progressBar}>
          <div 
            style={{
              ...styles.progressFill,
              width: `${getProgressPercentage()}%`
            }}
          />
        </div>
        
        {/* Error message */}
        {error && (
          <div style={styles.errorBox}>
            <strong>Registration Error:</strong>
            {error.includes('\n') ? (
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {error.split('\n').map((line, index) => (
                  <li key={index}>{line}</li>
                ))}
              </ul>
            ) : (
              <p style={{ marginTop: '4px' }}>{error}</p>
            )}
          </div>
        )}
        
        {!apiAvailable && (
          <div style={styles.warningBox}>
            <p><strong>Backend API is not available.</strong></p>
            <p>Please ensure the backend service is running according to the README instructions.</p>
          </div>
        )}
        
        {/* Tabs */}
        <div style={styles.tabContainer}>
          <button 
            style={{
              ...styles.tab,
              ...(activeTab === 'basic' ? styles.activeTab : {})
            }} 
            onClick={() => setActiveTab('basic')}
          >
            Basic Details
          </button>
          <button 
            style={{
              ...styles.tab,
              ...(activeTab === 'address' ? styles.activeTab : {})
            }} 
            onClick={() => setActiveTab('address')}
          >
            Address
          </button>
          <button 
            style={{
              ...styles.tab,
              ...(activeTab === 'insurance' ? styles.activeTab : {})
            }} 
            onClick={() => setActiveTab('insurance')}
          >
            Insurance
          </button>
          <button 
            style={{
              ...styles.tab,
              ...(activeTab === 'family' ? styles.activeTab : {})
            }} 
            onClick={() => setActiveTab('family')}
          >
            Family Members
          </button>
          <button 
            style={{
              ...styles.tab,
              ...(activeTab === 'mfa' ? styles.activeTab : {})
            }} 
            onClick={() => setActiveTab('mfa')}
          >
            MFA Setup
          </button>
        </div>
        
        {/* Basic Details Tab */}
        {activeTab === 'basic' && (
          <div style={styles.formSection}>
            {/* Profile Photo Upload - Moved to top */}
            <div style={styles.photoUploadContainer}>
              <div style={styles.photoPreviewContainer}>
                {formData.photoPreview ? (
                  <img 
                    src={formData.photoPreview} 
                    alt="Profile Preview" 
                    style={styles.photoPreview} 
                  />
                ) : (
                  <div style={styles.photoPlaceholder}>
                    Upload your profile photo
                  </div>
                )}
              </div>
              <input
                type="file"
                id="photo"
                name="photo"
                onChange={handleFileChange}
                accept="image/*"
                style={styles.fileInput}
              />
              <label htmlFor="photo" style={styles.photoUploadButton}>
                {formData.photo ? 'Change Photo' : 'Upload Photo'}
              </label>
              {formData.photo && (
                <p style={styles.fileInfo}>
                  Selected: {formData.photo.name}
                </p>
              )}

            </div>
            
            <h2 style={styles.subheading}>Personal Information</h2>
            <div style={styles.formGrid}>
              <div style={styles.formField}>
                <label style={styles.label}>
                  First Name <span style={styles.requiredField}>*</span>
                </label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  onBlur={() => setTouched({...touched, firstName: true})}
                  style={{
                    ...styles.input,
                    ...(touched.firstName && validationErrors.firstName ? styles.invalidInput : {})
                  }}
                  required
                />
                {touched.firstName && validationErrors.firstName && (
                  <div style={styles.fieldError}>{validationErrors.firstName}</div>
                )}
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>
                  Last Name <span style={styles.requiredField}>*</span>
                </label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  onBlur={() => setTouched({...touched, lastName: true})}
                  style={{
                    ...styles.input,
                    ...(touched.lastName && validationErrors.lastName ? styles.invalidInput : {})
                  }}
                  required
                />
                {touched.lastName && validationErrors.lastName && (
                  <div style={styles.fieldError}>{validationErrors.lastName}</div>
                )}
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Display Name</label>
                <input
                  type="text"
                  name="displayName"
                  value={formData.displayName}
                  onChange={handleInputChange}
                  style={styles.input}
                  placeholder="How you want to be addressed"
                />
                <p style={styles.infoText}>Leave blank to use your full name</p>
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Date of Birth</label>
                <input
                  type="date"
                  name="dateOfBirth"
                  value={formData.dateOfBirth}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Gender</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  style={styles.select}
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Blood Group</label>
                <select
                  name="bloodGroup"
                  value={formData.bloodGroup}
                  onChange={handleInputChange}
                  style={styles.select}
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
                  <option value="other">Other</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              
              {formData.bloodGroup === 'other' && (
                <div style={styles.formField}>
                  <label style={styles.label}>Custom Blood Group</label>
                  <input
                    type="text"
                    name="customBloodGroup"
                    value={formData.customBloodGroup}
                    onChange={handleInputChange}
                    style={styles.input}
                  />
                </div>
              )}
            </div>
            
            <h2 style={{...styles.subheading, marginTop: '24px'}}>Contact Information</h2>
            <div style={styles.formGrid}>
              <div style={styles.formField}>
                <label style={styles.label}>
                  Email <span style={styles.requiredField}>*</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  onBlur={() => setTouched({...touched, email: true})}
                  style={{
                    ...styles.input,
                    ...(touched.email && validationErrors.email ? styles.invalidInput : {})
                  }}
                  required
                />
                {touched.email && validationErrors.email && (
                  <div style={styles.fieldError}>{validationErrors.email}</div>
                )}
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>
                  Phone <span style={styles.requiredField}>*</span>
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  onBlur={() => setTouched({...touched, phone: true})}
                  style={{
                    ...styles.input,
                    ...(touched.phone && validationErrors.phone ? styles.invalidInput : {})
                  }}
                  required
                />
                {touched.phone && validationErrors.phone && (
                  <div style={styles.fieldError}>{validationErrors.phone}</div>
                )}
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Emergency Contact</label>
                <input
                  type="tel"
                  name="emergencyContact"
                  value={formData.emergencyContact}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
            </div>
            
            <h2 style={{...styles.subheading, marginTop: '24px'}}>Account Security</h2>
            <div style={styles.formGrid}>
              <div style={styles.formField}>
                <label style={styles.label}>
                  Password <span style={styles.requiredField}>*</span>
                </label>
                <div style={styles.passwordFieldContainer}>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    onBlur={() => setTouched({...touched, password: true})}
                    style={{
                      ...styles.input,
                      ...(touched.password && validationErrors.password ? styles.invalidInput : {})
                    }}
                    required
                  />
                  {showPasswordHints && (
                    <div style={styles.passwordHints}>
                      <p style={{marginTop: 0, marginBottom: '8px', fontWeight: '600', fontSize: '13px'}}>Password Requirements:</p>
                      <div style={{...styles.passwordHint, ...(passwordCriteria.length ? styles.validHint : styles.invalidHint)}}>
                        <span style={styles.passwordHintIcon}>{passwordCriteria.length ? '✓' : '○'}</span> 
                        At least 12 characters
                      </div>
                      <div style={{...styles.passwordHint, ...(passwordCriteria.uppercase ? styles.validHint : styles.invalidHint)}}>
                        <span style={styles.passwordHintIcon}>{passwordCriteria.uppercase ? '✓' : '○'}</span> 
                        At least one uppercase letter
                      </div>
                      <div style={{...styles.passwordHint, ...(passwordCriteria.lowercase ? styles.validHint : styles.invalidHint)}}>
                        <span style={styles.passwordHintIcon}>{passwordCriteria.lowercase ? '✓' : '○'}</span> 
                        At least one lowercase letter
                      </div>
                      <div style={{...styles.passwordHint, ...(passwordCriteria.number ? styles.validHint : styles.invalidHint)}}>
                        <span style={styles.passwordHintIcon}>{passwordCriteria.number ? '✓' : '○'}</span> 
                        At least one number
                      </div>
                      <div style={{...styles.passwordHint, ...(passwordCriteria.special ? styles.validHint : styles.invalidHint)}}>
                        <span style={styles.passwordHintIcon}>{passwordCriteria.special ? '✓' : '○'}</span> 
                        At least one special character
                      </div>
                    </div>
                  )}
                </div>
                {touched.password && validationErrors.password && (
                  <div style={styles.fieldError}>{validationErrors.password}</div>
                )}
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>
                  Confirm Password <span style={styles.requiredField}>*</span>
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  onBlur={() => setTouched({...touched, confirmPassword: true})}
                  style={{
                    ...styles.input,
                    ...(touched.confirmPassword && validationErrors.confirmPassword ? styles.invalidInput : {})
                  }}
                  required
                />
                {touched.confirmPassword && validationErrors.confirmPassword && (
                  <div style={styles.fieldError}>{validationErrors.confirmPassword}</div>
                )}
              </div>
            </div>
            
            <h2 style={{...styles.subheading, marginTop: '24px'}}>Identification</h2>
            <div style={styles.formGrid}>
              <div style={styles.formField}>
                <label style={styles.label}>Aadhar ID</label>
                <input
                  type="text"
                  name="aadharId"
                  value={formData.aadharId}
                  onChange={handleInputChange}
                  style={styles.input}
                  placeholder="XXXX-XXXX-XXXX"
                />
              </div>
            </div>
            
            <div style={styles.buttonContainer}>
              <div></div> {/* Empty div for spacing */}
              <button 
                style={{...styles.button, ...styles.primaryButton}} 
                onClick={handleNext}
              >
                Next: Address
              </button>
            </div>
          </div>
        )}
        
        {/* Address Tab */}
        {activeTab === 'address' && (
          <div style={styles.formSection}>
            <h2 style={styles.subheading}>Address Information</h2>
            <div style={styles.formGrid}>
              <div style={styles.formField}>
                <label style={styles.label}>Street Address</label>
                <input
                  type="text"
                  name="street"
                  value={formData.street}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>City</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>State</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>ZIP Code</label>
                <input
                  type="text"
                  name="zipCode"
                  value={formData.zipCode}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Country</label>
                <input
                  type="text"
                  name="country"
                  value={formData.country}
                  onChange={handleInputChange}
                  style={styles.input}
                />
              </div>
              
              <div style={styles.formField}>
                <label style={styles.label}>Address Type</label>
                <select
                  name="addressType"
                  value={formData.addressType}
                  onChange={handleInputChange}
                  style={styles.select}
                >
                  <option value="home">Home</option>
                  <option value="work">Work</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
            
            <div style={styles.buttonContainer}>
              <button 
                style={{...styles.button, ...styles.secondaryButton}} 
                onClick={handlePrevious}
              >
                Back: Basic Details
              </button>
              <button 
                style={{...styles.button, ...styles.primaryButton}} 
                onClick={handleNext}
              >
                Next: Family Members
              </button>
            </div>
          </div>
        )}
        
        {/* Insurance Tab */}
        {activeTab === 'insurance' && (
          <div style={styles.formSection}>
            <h2 style={styles.subheading}>Insurance Information</h2>
            
            <div style={styles.formField}>
              <label style={{...styles.label, display: 'flex', alignItems: 'center'}}>
                <input
                  type="checkbox"
                  name="hasInsurance"
                  checked={formData.hasInsurance}
                  onChange={handleInputChange}
                  style={{marginRight: '8px'}}
                />
                I have health insurance
              </label>
            </div>
            
            {formData.hasInsurance && (
              <>
                {formData.insuranceList.length > 0 && (
                  <div style={{marginBottom: '24px'}}>
                    <h3 style={{...styles.subheading, fontSize: '16px'}}>Your Insurance Plans</h3>
                    {formData.insuranceList.map(insurance => (
                      <div key={insurance.id} style={styles.insuranceCard}>
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                          <div>
                            <h4 style={{margin: '0 0 8px 0', fontWeight: '600'}}>
                              {insurance.insuranceCategory === 'private' ? 'Private' : 'Government'} Insurance
                            </h4>
                            <p style={{margin: '0 0 4px 0'}}>
                              <strong>Type:</strong> {insurance.displayName}
                            </p>
                            {insurance.providerName && (
                              <p style={{margin: '0 0 4px 0'}}>
                                <strong>Provider:</strong> {insurance.providerName}
                              </p>
                            )}
                            <p style={{margin: '0 0 4px 0'}}>
                              <strong>Policy Number:</strong> {insurance.policyNumber}
                            </p>
                          </div>
                          <div>
                            <button 
                              style={{...styles.button, ...styles.secondaryButton, marginRight: '8px', padding: '8px 16px'}} 
                              onClick={() => editInsurance(insurance)}
                            >
                              Edit
                            </button>
                            <button 
                              style={{...styles.button, ...styles.dangerButton, padding: '8px 16px'}} 
                              onClick={() => removeInsurance(insurance.id)}
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div style={styles.insuranceForm}>
                  <h3 style={{...styles.subheading, fontSize: '16px', marginTop: '0'}}>
                    {editingInsurance ? 'Edit Insurance Plan' : 'Add Insurance Plan'}
                  </h3>
                  
                  <div style={styles.formGrid}>
                    <div style={styles.formField}>
                      <label style={styles.label}>Insurance Category</label>
                      <select
                        name="insuranceCategory"
                        value={currentInsurance.insuranceCategory}
                        onChange={handleInsuranceInputChange}
                        style={styles.select}
                      >
                        <option value="">Select Category</option>
                        <option value="private">Private Insurance</option>
                        <option value="government">Government Scheme</option>
                      </select>
                    </div>
                    
                    {currentInsurance.insuranceCategory === 'private' && (
                      <div style={styles.formField}>
                        <label style={styles.label}>Insurance Type</label>
                        <select
                          name="insuranceType"
                          value={currentInsurance.insuranceType}
                          onChange={handleInsuranceInputChange}
                          style={styles.select}
                        >
                          <option value="">Select Type</option>
                          {privateInsuranceTypes.map(type => (
                            <option key={type} value={type}>{type}</option>
                          ))}
                          <option value="other">Other</option>
                        </select>
                      </div>
                    )}
                    
                    {currentInsurance.insuranceCategory === 'government' && (
                      <div style={styles.formField}>
                        <label style={styles.label}>Scheme Name</label>
                        <select
                          name="insuranceType"
                          value={currentInsurance.insuranceType}
                          onChange={handleInsuranceInputChange}
                          style={styles.select}
                        >
                          <option value="">Select Scheme</option>
                          {governmentInsuranceTypes.map(type => (
                            <option key={type} value={type}>{type}</option>
                          ))}
                          <option value="other">Other</option>
                        </select>
                      </div>
                    )}
                    
                    {currentInsurance.insuranceType === 'other' && (
                      <div style={styles.formField}>
                        <label style={styles.label}>Specify Insurance Type</label>
                        <input
                          type="text"
                          name="customType"
                          value={currentInsurance.customType}
                          onChange={handleInsuranceInputChange}
                          style={styles.input}
                        />
                      </div>
                    )}
                    
                    {currentInsurance.insuranceCategory === 'private' && (
                      <div style={styles.formField}>
                        <label style={styles.label}>Provider Name</label>
                        <input
                          type="text"
                          name="providerName"
                          value={currentInsurance.providerName}
                          onChange={handleInsuranceInputChange}
                          style={styles.input}
                        />
                      </div>
                    )}
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Policy Number</label>
                      <input
                        type="text"
                        name="policyNumber"
                        value={currentInsurance.policyNumber}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Group Number (if applicable)</label>
                      <input
                        type="text"
                        name="groupNumber"
                        value={currentInsurance.groupNumber}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Plan Type</label>
                      <input
                        type="text"
                        name="planType"
                        value={currentInsurance.planType}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                        placeholder="e.g., PPO, HMO, EPO"
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Effective Date</label>
                      <input
                        type="date"
                        name="effectiveDate"
                        value={currentInsurance.effectiveDate}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Expiration Date</label>
                      <input
                        type="date"
                        name="expirationDate"
                        value={currentInsurance.expirationDate}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Copay Amount</label>
                      <input
                        type="text"
                        name="copayAmount"
                        value={currentInsurance.copayAmount}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                        placeholder="e.g., ₹500"
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Deductible Amount</label>
                      <input
                        type="text"
                        name="deductibleAmount"
                        value={currentInsurance.deductibleAmount}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                        placeholder="e.g., ₹5000"
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Policy Holder Name</label>
                      <input
                        type="text"
                        name="policyHolderName"
                        value={currentInsurance.policyHolderName}
                        onChange={handleInsuranceInputChange}
                        style={styles.input}
                        placeholder="Leave blank if self"
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Relationship to Policy Holder</label>
                      <select
                        name="relationshipToPolicyHolder"
                        value={currentInsurance.relationshipToPolicyHolder}
                        onChange={handleInsuranceInputChange}
                        style={styles.select}
                      >
                        <option value="self">Self</option>
                        <option value="spouse">Spouse</option>
                        <option value="child">Child</option>
                        <option value="parent">Parent</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  
                  <div style={styles.formField}>
                    <label style={styles.label}>Insurance Card/Documents</label>
                    <input
                      type="file"
                      id="insuranceFiles"
                      onChange={handleInsuranceFileChange}
                      multiple
                      style={styles.fileInput}
                    />
                    <label htmlFor="insuranceFiles" style={styles.fileLabel}>
                      Upload Files
                    </label>
                    {currentInsurance.insuranceFiles.length > 0 && (
                      <div style={{marginTop: '12px'}}>
                        <p style={{fontWeight: '500', margin: '0 0 8px 0'}}>Selected Files:</p>
                        <ul style={{paddingLeft: '20px', margin: '0'}}>
                          {currentInsurance.insuranceFiles.map((file, index) => (
                            <li key={index} style={{marginBottom: '4px'}}>
                              {file.name}
                              <button
                                onClick={() => removeInsuranceFile(index)}
                                style={{
                                  marginLeft: '8px',
                                  background: 'none',
                                  border: 'none',
                                  color: '#ef4444',
                                  cursor: 'pointer',
                                  padding: '0',
                                  fontSize: '14px'
                                }}
                              >
                                Remove
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <div style={{marginTop: '16px'}}>
                    <button 
                      style={{...styles.button, ...styles.successButton}} 
                      onClick={addInsurance}
                      disabled={!((currentInsurance.insuranceCategory === 'government' || currentInsurance.providerName) && currentInsurance.policyNumber)}
                    >
                      {editingInsurance ? 'Update Insurance' : 'Add Insurance'}
                    </button>
                    {editingInsurance && (
                      <button 
                        style={{...styles.button, ...styles.secondaryButton, marginLeft: '12px'}} 
                        onClick={() => {
                          setEditingInsurance(null);
                          setCurrentInsurance({
                            insuranceCategory: '',
                            insuranceType: '',
                            customType: '',
                            providerName: '',
                            policyNumber: '',
                            groupNumber: '',
                            planType: '',
                            effectiveDate: '',
                            expirationDate: '',
                            copayAmount: '',
                            deductibleAmount: '',
                            policyHolderName: '',
                            relationshipToPolicyHolder: 'self',
                            insuranceFiles: []
                          });
                        }}
                      >
                        Cancel Editing
                      </button>
                    )}
                  </div>
                </div>
              </>
            )}
            
            <div style={styles.buttonContainer}>
              <button 
                style={{...styles.button, ...styles.secondaryButton}} 
                onClick={handlePrevious}
              >
                Back: Address
              </button>
              <button 
                style={{...styles.button, ...styles.primaryButton}} 
                onClick={handleNext}
              >
                Next: Family Members
              </button>
            </div>
          </div>
        )}
        
        {/* Family Members Tab */}
        {activeTab === 'family' && (
          <div style={styles.formSection}>
            <h2 style={styles.subheading}>Family Members</h2>
            
            <div style={styles.formField}>
              <label style={{...styles.label, display: 'flex', alignItems: 'center'}}>
                <input
                  type="checkbox"
                  checked={hasFamilyMembers}
                  onChange={(e) => setHasFamilyMembers(e.target.checked)}
                  style={{marginRight: '8px'}}
                />
                I want to add family members
              </label>
            </div>
            
            {hasFamilyMembers && (
              <>
                {familyMembers.length > 0 && (
                  <div style={{marginBottom: '24px'}}>
                    <h3 style={{...styles.subheading, fontSize: '16px'}}>Your Family Members</h3>
                    {familyMembers.map(member => (
                      <div key={member.id} style={styles.insuranceCard}>
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                          <div>
                            <h4 style={{margin: '0 0 8px 0', fontWeight: '600'}}>
                              {member.fullName}
                            </h4>
                            <p style={{margin: '0 0 4px 0'}}>
                              <strong>Relation:</strong> {member.relation}
                            </p>
                            <p style={{margin: '0 0 4px 0'}}>
                              <strong>Gender:</strong> {member.gender}
                            </p>
                            {member.contactNumber && (
                              <p style={{margin: '0 0 4px 0'}}>
                                <strong>Contact:</strong> {member.contactNumber}
                              </p>
                            )}
                            {member.aadhaarId && (
                              <p style={{margin: '0 0 4px 0'}}>
                                <strong>Aadhaar:</strong> ****-****-{member.aadhaarId.slice(-4)}
                              </p>
                            )}
                          </div>
                          <div>
                            <button 
                              style={{...styles.button, ...styles.secondaryButton, marginRight: '8px', padding: '8px 16px'}} 
                              onClick={() => editFamilyMember(member)}
                            >
                              Edit
                            </button>
                            <button 
                              style={{...styles.button, ...styles.dangerButton, padding: '8px 16px'}} 
                              onClick={() => removeFamilyMember(member.id)}
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div style={styles.insuranceForm}>
                  <h3 style={{...styles.subheading, fontSize: '16px', marginTop: '0'}}>
                    {editingFamilyMember ? 'Edit Family Member' : 'Add Family Member'}
                  </h3>
                  
                  <div style={styles.formGrid}>
                    <div style={styles.formField}>
                      <label style={styles.label}>Full Name *</label>
                      <input
                        type="text"
                        name="fullName"
                        value={currentFamilyMember.fullName}
                        onChange={handleFamilyMemberInputChange}
                        style={styles.input}
                        required
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Relation *</label>
                      <select
                        name="relation"
                        value={currentFamilyMember.relation}
                        onChange={handleFamilyMemberInputChange}
                        style={styles.select}
                        required
                      >
                        <option value="">Select Relation</option>
                        <option value="spouse">Spouse</option>
                        <option value="father">Father</option>
                        <option value="mother">Mother</option>
                        <option value="son">Son</option>
                        <option value="daughter">Daughter</option>
                        <option value="brother">Brother</option>
                        <option value="sister">Sister</option>
                        <option value="grandfather">Grandfather</option>
                        <option value="grandmother">Grandmother</option>
                        <option value="grandson">Grandson</option>
                        <option value="granddaughter">Granddaughter</option>
                        <option value="uncle">Uncle</option>
                        <option value="aunt">Aunt</option>
                        <option value="nephew">Nephew</option>
                        <option value="niece">Niece</option>
                        <option value="cousin">Cousin</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Gender *</label>
                      <select
                        name="gender"
                        value={currentFamilyMember.gender}
                        onChange={handleFamilyMemberInputChange}
                        style={styles.select}
                        required
                      >
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Contact Number</label>
                      <input
                        type="tel"
                        name="contactNumber"
                        value={currentFamilyMember.contactNumber}
                        onChange={handleFamilyMemberInputChange}
                        style={styles.input}
                        placeholder="10-digit phone number"
                      />
                    </div>
                    
                    <div style={styles.formField}>
                      <label style={styles.label}>Aadhaar ID</label>
                      <input
                        type="text"
                        name="aadhaarId"
                        value={currentFamilyMember.aadhaarId}
                        onChange={handleFamilyMemberInputChange}
                        style={styles.input}
                        placeholder="XXXX-XXXX-XXXX"
                        maxLength="12"
                      />
                    </div>
                  </div>
                  
                  <div style={{marginTop: '16px'}}>
                    <button 
                      style={{...styles.button, ...styles.successButton}} 
                      onClick={addFamilyMember}
                      disabled={!currentFamilyMember.fullName || !currentFamilyMember.relation || !currentFamilyMember.gender}
                    >
                      {editingFamilyMember ? 'Update Family Member' : 'Add Family Member'}
                    </button>
                    {editingFamilyMember && (
                      <button 
                        style={{...styles.button, ...styles.secondaryButton, marginLeft: '12px'}} 
                        onClick={() => {
                          setEditingFamilyMember(null);
                          setCurrentFamilyMember({
                            fullName: '',
                            relation: '',
                            gender: '',
                            contactNumber: '',
                            aadhaarId: ''
                          });
                        }}
                      >
                        Cancel Editing
                      </button>
                    )}
                  </div>
                </div>
              </>
            )}
            
            <div style={styles.buttonContainer}>
              <button 
                style={{...styles.button, ...styles.secondaryButton}} 
                onClick={handlePrevious}
              >
                Back: Insurance
              </button>
              <button 
                style={{...styles.button, ...styles.primaryButton}} 
                onClick={handleNext}
              >
                Next: MFA Setup
              </button>
            </div>
          </div>
        )}
        
        {/* MFA Setup Tab */}
        {activeTab === 'mfa' && (
          <div style={styles.formSection}>
            <h2 style={styles.subheading}>Multi-Factor Authentication</h2>
            
            <MFASetupTab formData={formData} handleInputChange={handleInputChange} />
            
            <div style={styles.buttonContainer}>
              <button 
                style={{...styles.button, ...styles.secondaryButton}} 
                onClick={handlePrevious}
              >
                Back: Family Members
              </button>
              <button 
                style={{...styles.button, ...styles.primaryButton}} 
                onClick={handleSave}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Registering...' : 'Complete Registration'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientRegistrationPage;