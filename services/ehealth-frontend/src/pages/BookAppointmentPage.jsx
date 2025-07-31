import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Clock, 
  ChevronLeft,
  Check
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import mockData from '../data/mockData';

const BookAppointmentPage = () => {
  const { hospitalId } = useParams();
  const navigate = useNavigate();
  const [activeMenu, setActiveMenu] = useState('hospitals');
  const [step, setStep] = useState(1); // 1: Select Doctor, 2: Select Time, 3: Confirm
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [hospital, setHospital] = useState(null);
  const [showNotification, setShowNotification] = useState(false);

  // Get available dates (next 7 days)
  const availableDates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i);
    return date;
  });

  // Mock time slots
  const morningSlots = ['09:00 AM', '10:00 AM', '11:00 AM'];
  const afternoonSlots = ['01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM'];
  const eveningSlots = ['05:00 PM', '06:00 PM', '07:00 PM'];

  useEffect(() => {
    // Get hospital data
    if (mockData.hospitals[hospitalId]) {
      setHospital(mockData.hospitals[hospitalId]);
    } else {
      // Default to first hospital if not found
      setHospital(mockData.hospitals['4']);
    }
  }, [hospitalId]);

  const handleDoctorSelect = (doctor) => {
    setSelectedDoctor(doctor);
    setStep(2);
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
  };

  const handleTimeSelect = (time) => {
    setSelectedTime(time);
  };

  const handleConfirm = () => {
    setStep(3);
  };

  const handleBookAppointment = () => {
    // In a real app, this would make an API call to book the appointment
    setShowNotification(true);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
      setShowNotification(false);
      // Navigate back to dashboard
      navigate('/patient-dashboard');
    }, 3000);
  };

  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };

  if (!hospital) {
    return (
      <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
        <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
          <Header userData={userData} />
          <main style={{ flex: 1, padding: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div>Loading...</div>
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
        
        {/* Notification */}
        {showNotification && (
          <div style={{
            position: 'fixed',
            top: '1rem',
            right: '1rem',
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1rem',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            zIndex: 50
          }}>
            <Check className="w-5 h-5" />
            <span>Appointment booked successfully!</span>
          </div>
        )}
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          {/* Breadcrumbs */}
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » Hospitals » {hospital.name} » Book Appointment
          </div>
          
          {/* Header */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            marginBottom: '1.5rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                  Book Appointment at {hospital.name}
                </h1>
                <p style={{ color: '#6b7280' }}>
                  {step === 1 ? 'Select a doctor to proceed' : 
                   step === 2 ? 'Select date and time for your appointment' : 
                   'Confirm your appointment details'}
                </p>
              </div>
              
              {/* Steps Indicator */}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <div style={{ 
                  width: '2rem', 
                  height: '2rem', 
                  borderRadius: '50%', 
                  backgroundColor: step >= 1 ? '#3b82f6' : '#e5e7eb',
                  color: step >= 1 ? 'white' : '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '600'
                }}>1</div>
                <div style={{ 
                  width: '2rem', 
                  height: '2rem', 
                  borderRadius: '50%', 
                  backgroundColor: step >= 2 ? '#3b82f6' : '#e5e7eb',
                  color: step >= 2 ? 'white' : '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '600'
                }}>2</div>
                <div style={{ 
                  width: '2rem', 
                  height: '2rem', 
                  borderRadius: '50%', 
                  backgroundColor: step >= 3 ? '#3b82f6' : '#e5e7eb',
                  color: step >= 3 ? 'white' : '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '600'
                }}>3</div>
              </div>
            </div>
          </div>
          
          {/* Step 1: Select Doctor */}
          {step === 1 && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827', marginBottom: '1.5rem' }}>
                Available Doctors
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                {hospital.doctors.map(doctor => (
                  <div 
                    key={doctor.id} 
                    style={{
                      backgroundColor: '#f8fafc',
                      borderRadius: '0.75rem',
                      border: '1px solid #e5e7eb',
                      padding: '1.5rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onClick={() => handleDoctorSelect(doctor)}
                    onMouseOver={(e) => {
                      e.currentTarget.style.backgroundColor = '#f1f5f9';
                      e.currentTarget.style.borderColor = '#3b82f6';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.backgroundColor = '#f8fafc';
                      e.currentTarget.style.borderColor = '#e5e7eb';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <img 
                        src={doctor.photo} 
                        alt={doctor.name} 
                        style={{ width: '64px', height: '64px', borderRadius: '50%', objectFit: 'cover' }} 
                      />
                      <div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '0.25rem' }}>
                          {doctor.name}
                        </h3>
                        <p style={{ fontSize: '0.875rem', color: '#3b82f6', marginBottom: '0.5rem' }}>
                          {doctor.specialty}
                        </p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <span style={{ color: '#fbbf24' }}>★</span>
                          <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#111827' }}>{doctor.rating}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Step 2: Select Date and Time */}
          {step === 2 && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                <button 
                  onClick={() => setStep(1)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: 'transparent',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    color: '#6b7280',
                    cursor: 'pointer'
                  }}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Back
                </button>
                
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.25rem' }}>
                    Select Date & Time
                  </h2>
                  <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    Appointment with {selectedDoctor.name}
                  </p>
                </div>
              </div>
              
              {/* Date Selection */}
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>
                  <Calendar className="w-4 h-4 inline mr-2" />
                  Select Date
                </h3>
                
                <div style={{ display: 'flex', gap: '0.75rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                  {availableDates.map((date, index) => {
                    const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();
                    const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
                    const dayNumber = date.getDate();
                    const month = date.toLocaleDateString('en-US', { month: 'short' });
                    
                    return (
                      <div 
                        key={index}
                        onClick={() => handleDateSelect(date)}
                        style={{
                          minWidth: '5rem',
                          padding: '0.75rem',
                          borderRadius: '0.5rem',
                          backgroundColor: isSelected ? '#3b82f6' : '#f8fafc',
                          color: isSelected ? 'white' : '#111827',
                          border: `1px solid ${isSelected ? '#3b82f6' : '#e5e7eb'}`,
                          textAlign: 'center',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                      >
                        <div style={{ fontWeight: '600', fontSize: '0.875rem' }}>{dayName}</div>
                        <div style={{ fontWeight: '700', fontSize: '1.25rem', margin: '0.25rem 0' }}>{dayNumber}</div>
                        <div style={{ fontSize: '0.75rem' }}>{month}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              {/* Time Selection */}
              {selectedDate && (
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>
                    <Clock className="w-4 h-4 inline mr-2" />
                    Select Time
                  </h3>
                  
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.75rem' }}>Morning</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                      {morningSlots.map((time, index) => {
                        const isSelected = selectedTime === time;
                        
                        return (
                          <div 
                            key={index}
                            onClick={() => handleTimeSelect(time)}
                            style={{
                              padding: '0.5rem 1rem',
                              borderRadius: '0.5rem',
                              backgroundColor: isSelected ? '#3b82f6' : '#f8fafc',
                              color: isSelected ? 'white' : '#111827',
                              border: `1px solid ${isSelected ? '#3b82f6' : '#e5e7eb'}`,
                              fontSize: '0.875rem',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                          >
                            {time}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.75rem' }}>Afternoon</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                      {afternoonSlots.map((time, index) => {
                        const isSelected = selectedTime === time;
                        
                        return (
                          <div 
                            key={index}
                            onClick={() => handleTimeSelect(time)}
                            style={{
                              padding: '0.5rem 1rem',
                              borderRadius: '0.5rem',
                              backgroundColor: isSelected ? '#3b82f6' : '#f8fafc',
                              color: isSelected ? 'white' : '#111827',
                              border: `1px solid ${isSelected ? '#3b82f6' : '#e5e7eb'}`,
                              fontSize: '0.875rem',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                          >
                            {time}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  
                  <div style={{ marginBottom: '2rem' }}>
                    <h4 style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.75rem' }}>Evening</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                      {eveningSlots.map((time, index) => {
                        const isSelected = selectedTime === time;
                        
                        return (
                          <div 
                            key={index}
                            onClick={() => handleTimeSelect(time)}
                            style={{
                              padding: '0.5rem 1rem',
                              borderRadius: '0.5rem',
                              backgroundColor: isSelected ? '#3b82f6' : '#f8fafc',
                              color: isSelected ? 'white' : '#111827',
                              border: `1px solid ${isSelected ? '#3b82f6' : '#e5e7eb'}`,
                              fontSize: '0.875rem',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                          >
                            {time}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  
                  <button
                    onClick={handleConfirm}
                    disabled={!selectedTime}
                    style={{
                      padding: '0.75rem 1.5rem',
                      backgroundColor: selectedTime ? '#3b82f6' : '#e5e7eb',
                      color: selectedTime ? 'white' : '#9ca3af',
                      border: 'none',
                      borderRadius: '0.5rem',
                      fontWeight: '600',
                      cursor: selectedTime ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s'
                    }}
                  >
                    Continue
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Step 3: Confirm */}
          {step === 3 && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                <button 
                  onClick={() => setStep(2)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: 'transparent',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                    color: '#6b7280',
                    cursor: 'pointer'
                  }}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Back
                </button>
                
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.25rem' }}>
                    Confirm Appointment
                  </h2>
                  <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    Please review your appointment details
                  </p>
                </div>
              </div>
              
              <div style={{ 
                backgroundColor: '#f8fafc', 
                borderRadius: '0.75rem', 
                padding: '1.5rem',
                marginBottom: '2rem',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem' }}>
                  <img 
                    src={selectedDoctor.photo} 
                    alt={selectedDoctor.name} 
                    style={{ width: '80px', height: '80px', borderRadius: '50%', objectFit: 'cover' }} 
                  />
                  
                  <div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '0.25rem' }}>
                      {selectedDoctor.name}
                    </h3>
                    <p style={{ fontSize: '0.875rem', color: '#3b82f6', marginBottom: '0.5rem' }}>
                      {selectedDoctor.specialty}
                    </p>
                    <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {hospital.name}
                    </p>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '2rem' }}>
                  <div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>Date</div>
                    <div style={{ fontWeight: '600', color: '#111827' }}>
                      {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                    </div>
                  </div>
                  
                  <div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>Time</div>
                    <div style={{ fontWeight: '600', color: '#111827' }}>{selectedTime}</div>
                  </div>
                </div>
              </div>
              
              <button
                onClick={handleBookAppointment}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                Book Appointment
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default BookAppointmentPage;