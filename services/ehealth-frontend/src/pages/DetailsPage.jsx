import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import mockData from '../data/mockData';
import { 
  MapPin, 
  Phone, 
  Mail, 
  Clock, 
  Award, 
  Star, 
  Calendar, 
  ShoppingBag,
  MessageSquare,
  Send
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

// Using imported mockData
// The following is kept for reference only
const mockDataReference = {
  hospitals: {
    4: {
      id: 4,
      name: 'Apollo Hospital',
      type: 'hospital',
      photo: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
      title: 'Multi-Specialty Hospital',
      description: 'Apollo Hospital is a leading multi-specialty hospital with state-of-the-art facilities.',
      hours: '24/7 Emergency Services',
      rating: 4.7,
      awards: ['Best Hospital 2023', 'Excellence in Patient Care'],
      address: '21 Greams Lane, Off Greams Road, Chennai',
      phone: '+91 44 2829 3333',
      email: 'info@apollohospital.com',
      doctors: [
        { id: 1, name: 'Dr. Rajesh Kumar', specialty: 'Cardiologist', rating: 4.8, photo: 'https://randomuser.me/api/portraits/men/1.jpg' },
        { id: 2, name: 'Dr. Priya Sharma', specialty: 'Neurologist', rating: 4.9, photo: 'https://randomuser.me/api/portraits/women/2.jpg' }
      ],
      services: [
        { name: 'Emergency Care', description: '24/7 emergency medical services' },
        { name: 'Cardiology', description: 'Comprehensive heart care services' }
      ],
      about: 'Apollo Hospital has been at the forefront of healthcare excellence for over 30 years.'
    },
    5: {
      id: 5,
      name: 'Fortis Hospital',
      type: 'hospital',
      photo: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
      title: 'Multi-Specialty Hospital',
      description: 'Fortis Hospital provides comprehensive healthcare services with experienced professionals.',
      hours: '24/7 Emergency Services',
      rating: 4.5,
      awards: ['Excellence in Healthcare 2022'],
      address: 'Sector 62, Phase VIII, Mohali',
      phone: '+91 172 496 7000',
      email: 'info@fortishospital.com',
      doctors: [
        { id: 3, name: 'Dr. Amit Patel', specialty: 'Orthopedic', rating: 4.7, photo: 'https://randomuser.me/api/portraits/men/3.jpg' }
      ],
      services: [
        { name: 'Orthopedics', description: 'Complete bone and joint care' },
        { name: 'Pediatrics', description: 'Child healthcare services' }
      ],
      about: 'Fortis Hospital is committed to providing quality healthcare services to all patients.'
    },
    1: {
      id: 1,
      name: 'Apollo Hospital',
      type: 'hospital',
      photo: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
      title: 'Multi-Specialty Hospital',
      description: 'Apollo Hospital is a leading multi-specialty hospital providing comprehensive healthcare services with state-of-the-art facilities and experienced medical professionals.',
      hours: '24/7 Emergency Services',
      rating: 4.7,
      awards: ['Best Hospital 2023', 'Excellence in Patient Care', 'Top Medical Facility'],
      address: '21 Greams Lane, Off Greams Road, Chennai',
      phone: '+91 44 2829 3333',
      email: 'info@apollohospital.com',
      doctors: [
        { id: 1, name: 'Dr. Rajesh Kumar', specialty: 'Cardiologist', rating: 4.8, photo: 'https://randomuser.me/api/portraits/men/1.jpg' },
        { id: 2, name: 'Dr. Priya Sharma', specialty: 'Neurologist', rating: 4.9, photo: 'https://randomuser.me/api/portraits/women/2.jpg' },
        { id: 3, name: 'Dr. Amit Patel', specialty: 'Orthopedic Surgeon', rating: 4.7, photo: 'https://randomuser.me/api/portraits/men/3.jpg' }
      ],
      services: [
        { name: 'Emergency Care', description: '24/7 emergency medical services' },
        { name: 'Cardiology', description: 'Comprehensive heart care services' },
        { name: 'Neurology', description: 'Advanced neurological treatments' },
        { name: 'Orthopedics', description: 'Complete bone and joint care' },
        { name: 'Oncology', description: 'Cancer diagnosis and treatment' },
        { name: 'Pediatrics', description: 'Child healthcare services' }
      ],
      about: 'Apollo Hospital has been at the forefront of healthcare excellence for over 30 years. Our mission is to bring healthcare of international standards within the reach of every individual. We are committed to the achievement and maintenance of excellence in education, research and healthcare for the benefit of humanity.'
    }
  },
  doctors: {
    1: {
      id: 1,
      name: 'Dr. Rajesh Kumar',
      type: 'doctor',
      photo: 'https://randomuser.me/api/portraits/men/1.jpg',
      title: 'Senior Cardiologist',
      description: 'Dr. Rajesh Kumar is a renowned cardiologist with over 20 years of experience in treating heart diseases and performing cardiac surgeries.',
      hours: 'Mon-Fri: 9:00 AM - 5:00 PM',
      rating: 4.8,
      awards: ['Best Doctor Award 2022', 'Excellence in Cardiology', 'Research Pioneer'],
      hospital: 'Apollo Hospital',
      phone: '+91 98765 43210',
      email: 'dr.rajesh@apollohospital.com',
      qualifications: ['MBBS', 'MD Cardiology', 'Fellowship in Interventional Cardiology'],
      experience: '20+ years',
      specializations: ['Interventional Cardiology', 'Heart Failure Management', 'Cardiac Rehabilitation'],
      about: 'Dr. Rajesh Kumar is a distinguished cardiologist with extensive experience in diagnosing and treating various heart conditions. He specializes in interventional cardiology and has performed over 5,000 successful cardiac procedures. Dr. Kumar is known for his patient-centric approach and commitment to providing the highest quality of care.'
    }
  },
  pharmacies: {
    1: {
      id: 1,
      name: 'MedPlus Pharmacy',
      type: 'pharmacy',
      photo: 'https://images.unsplash.com/photo-1573883431205-98b5f10aaedb?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
      title: '24/7 Pharmacy Services',
      description: 'MedPlus Pharmacy offers a wide range of medicines, health products, and wellness items with home delivery options.',
      hours: 'Open 24/7',
      rating: 4.6,
      awards: ['Best Pharmacy Chain 2023', 'Customer Service Excellence'],
      address: '123 Health Street, Downtown',
      phone: '+91 98765 12345',
      email: 'care@medpluspharmacy.com',
      services: [
        { name: 'Prescription Filling', description: 'Quick and accurate prescription services' },
        { name: 'Home Delivery', description: 'Medicines delivered to your doorstep' },
        { name: 'Health Products', description: 'Wide range of health and wellness products' },
        { name: 'Health Consultations', description: 'Basic health consultations with pharmacists' }
      ],
      about: 'MedPlus Pharmacy is one of the leading pharmacy chains committed to providing high-quality medicines and healthcare products. We ensure that all medicines are sourced from reliable manufacturers and stored under optimal conditions to maintain their efficacy.'
    }
  },
  labs: {
    1: {
      id: 1,
      name: 'City Diagnostics',
      type: 'lab',
      photo: 'https://images.unsplash.com/photo-1579154204601-01588f351e67?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
      title: 'Advanced Diagnostic Center',
      description: 'City Diagnostics offers comprehensive laboratory testing services with state-of-the-art equipment and experienced technicians.',
      hours: 'Mon-Sat: 7:00 AM - 9:00 PM, Sun: 8:00 AM - 2:00 PM',
      rating: 4.5,
      awards: ['Accredited Laboratory', 'Quality Excellence Award'],
      address: '456 Medical Avenue, Uptown',
      phone: '+91 98765 67890',
      email: 'info@citydiagnostics.com',
      services: [
        { name: 'Blood Tests', description: 'Complete blood work and analysis' },
        { name: 'Imaging Services', description: 'X-ray, CT scan, MRI, and ultrasound' },
        { name: 'Pathology', description: 'Comprehensive pathological examinations' },
        { name: 'Home Sample Collection', description: 'Convenient sample collection at home' },
        { name: 'Health Packages', description: 'Preventive health checkup packages' }
      ],
      about: 'City Diagnostics is equipped with the latest technology and staffed by experienced professionals to provide accurate and reliable diagnostic services. We are committed to delivering timely results with a focus on quality and patient comfort.'
    }
  }
};

const DetailsPage = () => {
  const { type, id } = useParams();
  const [entity, setEntity] = useState(null);
  const [activeMenu, setActiveMenu] = useState(type);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // In a real app, this would be an API call
    console.log('Looking for:', type, id);
    
    // Always use a valid entity
    if (type === 'hospitals') {
      // For hospitals, use the entity with matching ID or default to ID 4
      const hospitalId = mockData.hospitals[id] ? id : '4';
      setEntity(mockData.hospitals[hospitalId]);
    } else if (type === 'doctors') {
      setEntity(mockData.doctors['1']);
    } else if (type === 'pharmacies') {
      setEntity(mockData.pharmacies['1']);
    } else if (type === 'labs') {
      setEntity(mockData.labs['1']);
    }
  }, [type, id]);

  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };

  if (!entity) {
    return (
      <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
        <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
          <Header userData={userData} />
          <main style={{ flex: 1, padding: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div style={{ 
              backgroundColor: 'white',
              borderRadius: '0.75rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              textAlign: 'center',
              maxWidth: '400px'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '1rem' }}>Loading Details</h2>
              <p style={{ color: '#6b7280' }}>Please wait while we fetch the information...</p>
              <button 
                onClick={() => window.history.back()}
                style={{
                  marginTop: '1.5rem',
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Go Back
              </button>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        <Header userData={userData} />
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          {/* Breadcrumbs */}
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » {type.charAt(0).toUpperCase() + type.slice(1)} » {entity.name}
          </div>
          
          {/* Header Section */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            overflow: 'hidden',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            marginBottom: '1.5rem'
          }}>
            <div style={{ 
              height: '200px', 
              backgroundImage: `url(${entity.photo})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              position: 'relative'
            }}>
              <div style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                padding: '2rem',
                background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%)',
                color: 'white'
              }}>
                <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{entity.name}</h1>
                <div style={{ fontSize: '1rem' }}>{entity.title}</div>
              </div>
            </div>
            
            <div style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                <div>
                  <div style={{ marginBottom: '1rem' }}>
                    <p style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.5' }}>{entity.description}</p>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Clock className="w-5 h-5 text-blue-600" />
                      <span style={{ color: '#4b5563' }}>{entity.hours}</span>
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Star className="w-5 h-5 text-yellow-500" />
                      <span style={{ fontWeight: '600' }}>{entity.rating}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  {entity.awards && entity.awards.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {entity.awards.map((award, index) => (
                        <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Award className="w-4 h-4 text-yellow-500" />
                          <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>{award}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Main Content */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Left Column */}
            <div>
              {/* Photos Section */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                marginBottom: '1.5rem'
              }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '1.5rem' }}>Photos</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                  <img src={entity.photo} alt={entity.name} style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '0.5rem' }} />
                  <img src={entity.photo} alt={entity.name} style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '0.5rem' }} />
                  <img src={entity.photo} alt={entity.name} style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '0.5rem' }} />
                </div>
              </div>
              
              {/* Doctors Section (Only for Hospitals) */}
              {entity.type === 'hospital' && entity.doctors && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '1rem',
                  padding: '2rem',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>Top Doctors</h2>
                    <Link to="/doctors" style={{ color: '#3b82f6', fontWeight: '500', textDecoration: 'none' }}>View All</Link>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                    {entity.doctors.map(doctor => (
                      <div key={doctor.id} style={{
                        backgroundColor: '#f8fafc',
                        borderRadius: '0.75rem',
                        border: '1px solid #e5e7eb',
                        padding: '1.5rem',
                        transition: 'all 0.2s',
                        cursor: 'pointer'
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.backgroundColor = '#f1f5f9';
                        e.currentTarget.style.borderColor = '#3b82f6';
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.backgroundColor = '#f8fafc';
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                      >
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                          <img src={doctor.photo} alt={doctor.name} style={{ width: '80px', height: '80px', borderRadius: '50%', marginBottom: '1rem' }} />
                          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '0.25rem' }}>{doctor.name}</h3>
                          <div style={{ fontSize: '0.875rem', color: '#3b82f6', marginBottom: '0.5rem' }}>{doctor.specialty}</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <Star className="w-4 h-4 text-yellow-500" />
                            <span style={{ fontWeight: '600', color: '#111827' }}>{doctor.rating}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Services Section (For Hospital, Pharmacy, Lab) */}
              {entity.services && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '1rem',
                  padding: '2rem',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                  marginBottom: '1.5rem'
                }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '1.5rem' }}>Our Services</h2>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                    {entity.services.map((service, index) => (
                      <div key={index} style={{
                        backgroundColor: '#f8fafc',
                        borderRadius: '0.75rem',
                        border: '1px solid #e5e7eb',
                        padding: '1.5rem'
                      }}>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '0.5rem' }}>{service.name}</h3>
                        <p style={{ fontSize: '0.875rem', color: '#4b5563' }}>{service.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* About Section */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                marginBottom: '1.5rem'
              }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '1.5rem' }}>About Us</h2>
                <p style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.7' }}>{entity.about}</p>
                
                {/* Doctor Specific Information */}
                {entity.type === 'doctor' && (
                  <div style={{ marginTop: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Qualifications</h3>
                    <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginBottom: '1.5rem' }}>
                      {entity.qualifications.map((qual, index) => (
                        <li key={index} style={{ fontSize: '0.875rem', color: '#4b5563', marginBottom: '0.5rem' }}>{qual}</li>
                      ))}
                    </ul>
                    
                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Specializations</h3>
                    <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem' }}>
                      {entity.specializations.map((spec, index) => (
                        <li key={index} style={{ fontSize: '0.875rem', color: '#4b5563', marginBottom: '0.5rem' }}>{spec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              {/* Map (For Hospital, Pharmacy, Lab) */}
              {(entity.type === 'hospital' || entity.type === 'pharmacy' || entity.type === 'lab') && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '1rem',
                  padding: '2rem',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                  marginBottom: '1.5rem'
                }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827', marginBottom: '1.5rem' }}>Location</h2>
                  
                  {/* Placeholder for Google Maps */}
                  <div style={{
                    width: '100%',
                    height: '200px',
                    backgroundColor: '#e5e7eb',
                    borderRadius: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#6b7280',
                    marginBottom: '1rem'
                  }}>
                    Map Placeholder
                  </div>
                  
                  <div style={{ fontSize: '0.875rem', color: '#4b5563' }}>
                    <strong>Address:</strong> {entity.address}
                  </div>
                </div>
              )}
            </div>
            
            {/* Right Column */}
            <div>
              {/* Action Card */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                marginBottom: '1.5rem',
                position: 'sticky',
                top: '1.5rem'
              }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827', marginBottom: '1.5rem' }}>
                  {entity.type === 'hospital' || entity.type === 'doctor' ? 'Book Appointment' : 
                   entity.type === 'pharmacy' ? 'Order Medicines' : 'Book Test'}
                </h2>
                
                <button style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  marginBottom: '1.5rem'
                }}>
                  {entity.type === 'hospital' || entity.type === 'doctor' ? <Calendar className="w-5 h-5" /> : 
                   entity.type === 'pharmacy' ? <ShoppingBag className="w-5 h-5" /> : <Calendar className="w-5 h-5" />}
                  {entity.type === 'hospital' || entity.type === 'doctor' ? 'Book Appointment' : 
                   entity.type === 'pharmacy' ? 'Order Medicines' : 'Book Test'}
                </button>
                
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Contact Information</h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {(entity.type === 'hospital' || entity.type === 'pharmacy' || entity.type === 'lab') && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <MapPin className="w-5 h-5 text-gray-500" />
                        <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>{entity.address}</span>
                      </div>
                    )}
                    
                    {entity.type === 'doctor' && entity.hospital && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Hospital className="w-5 h-5 text-gray-500" />
                        <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>{entity.hospital}</span>
                      </div>
                    )}
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <Phone className="w-5 h-5 text-gray-500" />
                      <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>{entity.phone}</span>
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <Mail className="w-5 h-5 text-gray-500" />
                      <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>{entity.email}</span>
                    </div>
                  </div>
                </div>
                
                {/* Message Box (Only for Doctors) */}
                {entity.type === 'doctor' && (
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Send Message</h3>
                    
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Type your message here..."
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        marginBottom: '1rem',
                        minHeight: '100px',
                        resize: 'vertical'
                      }}
                    />
                    
                    <button style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      backgroundColor: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.5rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}>
                      <Send className="w-5 h-5" />
                      Send Message
                    </button>
                  </div>
                )}
              </div>
              

            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DetailsPage;