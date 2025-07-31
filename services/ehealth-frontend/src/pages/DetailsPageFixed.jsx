import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import BookAppointmentButton from '../pages/BookAppointmentButton';
import TestBookingButton from '../pages/TestBookingButton';
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
  Send,
  Hospital
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import mockData from '../data/mockData';

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
                
                <Link 
                  to="/book-appointment/4"
                  style={{
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
                    marginBottom: '1.5rem',
                    textDecoration: 'none'
                  }}
                >
                  <Calendar className="w-5 h-5" />
                  Book Appointment (Direct Link)
                </Link>
                
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