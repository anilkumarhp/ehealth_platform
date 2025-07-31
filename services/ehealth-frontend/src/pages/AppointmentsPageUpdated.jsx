import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { Search, Calendar, Clock, MapPin, Plus, Minus, Trash } from 'lucide-react';

const AppointmentsPageUpdated = () => {
  const [activeMenu, setActiveMenu] = useState('appointments');
  const [activeTab, setActiveTab] = useState('book');
  const [activeBookingTab, setActiveBookingTab] = useState('hospital');
  const [showBookingForm, setShowBookingForm] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [bookingStep, setBookingStep] = useState(1);
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedPharmacy, setSelectedPharmacy] = useState(null);
  const [selectedLab, setSelectedLab] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [selectedMedicines, setSelectedMedicines] = useState([]);
  const [selectedTests, setSelectedTests] = useState([]);
  const [medicineQuantities, setMedicineQuantities] = useState({});
  
  // Load entity data from sessionStorage if available
  useEffect(() => {
    const entityType = sessionStorage.getItem('selectedEntityType');
    const entityData = sessionStorage.getItem('selectedEntityData');
    
    if (entityType && entityData) {
      setActiveBookingTab(entityType);
      
      const parsedData = JSON.parse(entityData);
      
      switch(entityType) {
        case 'hospital':
          setSelectedHospital(parsedData);
          setBookingStep(2);
          break;
        case 'doctor':
          setSelectedDoctor(parsedData);
          setBookingStep(2);
          break;
        case 'pharmacy':
          setSelectedPharmacy(parsedData);
          setBookingStep(2);
          break;
        case 'lab':
          setSelectedLab(parsedData);
          setBookingStep(2);
          break;
        default:
          break;
      }
      
      // Clear sessionStorage after use
      sessionStorage.removeItem('selectedEntityType');
      sessionStorage.removeItem('selectedEntityData');
    }
  }, []);
  
  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };
  
  // Mock data
  const upcomingAppointments = [
    {
      id: 1,
      type: 'doctor',
      name: 'Dr. Rajesh Kumar',
      specialty: 'Cardiologist',
      location: 'Apollo Hospital, Chennai',
      date: '15 June 2023',
      time: '10:00 AM',
      status: 'confirmed'
    },
    {
      id: 2,
      type: 'lab',
      name: 'Blood Test',
      location: 'City Diagnostics, Delhi',
      date: '18 June 2023',
      time: '09:30 AM',
      status: 'confirmed'
    }
  ];
  
  const previousAppointments = [
    {
      id: 3,
      type: 'doctor',
      name: 'Dr. Priya Sharma',
      specialty: 'Neurologist',
      location: 'Fortis Hospital, Delhi',
      date: '5 May 2023',
      time: '11:00 AM',
      status: 'completed'
    },
    {
      id: 4,
      type: 'pharmacy',
      name: 'Medicine Pickup',
      location: 'MedPlus Pharmacy, Mumbai',
      date: '2 May 2023',
      time: '03:00 PM',
      status: 'completed'
    }
  ];
  
  const hospitals = [
    { id: 1, name: 'Apollo Hospital', location: 'Chennai' },
    { id: 2, name: 'Fortis Hospital', location: 'Delhi' },
    { id: 3, name: 'Max Hospital', location: 'Mumbai' }
  ];
  
  const doctors = [
    { id: 1, name: 'Dr. Rajesh Kumar', specialty: 'Cardiologist', hospital: 'Apollo Hospital' },
    { id: 2, name: 'Dr. Priya Sharma', specialty: 'Neurologist', hospital: 'Fortis Hospital' },
    { id: 3, name: 'Dr. Amit Patel', specialty: 'Orthopedic', hospital: 'Max Hospital' }
  ];
  
  const pharmacies = [
    { id: 1, name: 'MedPlus Pharmacy', location: 'Chennai' },
    { id: 2, name: 'Apollo Pharmacy', location: 'Delhi' },
    { id: 3, name: 'Wellness Forever', location: 'Mumbai' }
  ];
  
  const medicines = [
    { id: 1, name: 'Paracetamol', type: 'Tablet', price: '₹20' },
    { id: 2, name: 'Amoxicillin', type: 'Capsule', price: '₹50' },
    { id: 3, name: 'Cetirizine', type: 'Tablet', price: '₹30' }
  ];
  
  const labs = [
    { id: 1, name: 'City Diagnostics', location: 'Chennai' },
    { id: 2, name: 'SRL Diagnostics', location: 'Delhi' },
    { id: 3, name: 'Thyrocare', location: 'Mumbai' }
  ];
  
  const labTests = [
    { id: 1, name: 'Complete Blood Count', price: '₹500' },
    { id: 2, name: 'Lipid Profile', price: '₹800' },
    { id: 3, name: 'Thyroid Function Test', price: '₹1200' }
  ];
  
  const timeSlots = [
    '09:00 AM', '10:00 AM', '11:00 AM', 
    '01:00 PM', '02:00 PM', '03:00 PM'
  ];
  
  const filteredHospitals = searchTerm 
    ? hospitals.filter(h => h.name.toLowerCase().includes(searchTerm.toLowerCase()))
    : hospitals;
    
  const filteredDoctors = searchTerm 
    ? doctors.filter(d => d.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         d.specialty.toLowerCase().includes(searchTerm.toLowerCase()))
    : doctors;
    
  const filteredPharmacies = searchTerm
    ? pharmacies.filter(p => p.name.toLowerCase().includes(searchTerm.toLowerCase()))
    : pharmacies;
    
  const filteredMedicines = searchTerm
    ? medicines.filter(m => m.name.toLowerCase().includes(searchTerm.toLowerCase()))
    : medicines;
    
  const filteredLabs = searchTerm
    ? labs.filter(l => l.name.toLowerCase().includes(searchTerm.toLowerCase()))
    : labs;
    
  const filteredLabTests = searchTerm
    ? labTests.filter(t => t.name.toLowerCase().includes(searchTerm.toLowerCase()))
    : labTests;
    
  const hospitalDoctors = selectedHospital 
    ? doctors.filter(d => d.hospital === selectedHospital.name)
    : [];
  
  const handleBookAppointment = () => {
    // In a real app, this would make an API call
    alert('Appointment booked successfully!');
    setShowBookingForm(false);
    setActiveTab('upcoming');
    resetBookingState();
  };
  
  const resetBookingState = () => {
    setBookingStep(1);
    setSelectedHospital(null);
    setSelectedDoctor(null);
    setSelectedPharmacy(null);
    setSelectedLab(null);
    setSelectedTime(null);
    setSelectedMedicines([]);
    setSelectedTests([]);
    setMedicineQuantities({});
    setSearchTerm('');
  };
  
  const toggleMedicineSelection = (medicine) => {
    const isSelected = selectedMedicines.some(m => m.id === medicine.id);
    
    if (isSelected) {
      setSelectedMedicines(selectedMedicines.filter(m => m.id !== medicine.id));
      const newQuantities = {...medicineQuantities};
      delete newQuantities[medicine.id];
      setMedicineQuantities(newQuantities);
    } else {
      setSelectedMedicines([...selectedMedicines, medicine]);
      setMedicineQuantities({...medicineQuantities, [medicine.id]: 1});
    }
  };
  
  const updateMedicineQuantity = (medicineId, change) => {
    const currentQuantity = medicineQuantities[medicineId] || 1;
    const newQuantity = Math.max(1, currentQuantity + change);
    setMedicineQuantities({...medicineQuantities, [medicineId]: newQuantity});
  };
  
  const toggleTestSelection = (test) => {
    const isSelected = selectedTests.some(t => t.id === test.id);
    
    if (isSelected) {
      setSelectedTests(selectedTests.filter(t => t.id !== test.id));
    } else {
      setSelectedTests([...selectedTests, test]);
    }
  };
  
  const renderAppointmentCard = (appointment) => (
    <div 
      key={appointment.id}
      style={{
        backgroundColor: 'white',
        borderRadius: '0.75rem',
        border: '1px solid #e5e7eb',
        padding: '1.5rem',
        marginBottom: '1rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
          {appointment.name}
        </h3>
        <span style={{
          fontSize: '0.75rem',
          backgroundColor: appointment.status === 'confirmed' ? '#dcfce7' : '#f1f5f9',
          color: appointment.status === 'confirmed' ? '#166534' : '#475569',
          padding: '0.25rem 0.5rem',
          borderRadius: '0.25rem'
        }}>
          {appointment.status === 'confirmed' ? 'Upcoming' : 'Completed'}
        </span>
      </div>
      
      {appointment.specialty && (
        <div style={{ fontSize: '0.875rem', color: '#3b82f6', marginBottom: '0.5rem' }}>
          {appointment.specialty}
        </div>
      )}
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <MapPin className="w-4 h-4 text-gray-500" />
        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{appointment.location}</span>
      </div>
      
      <div style={{ display: 'flex', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Calendar className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{appointment.date}</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Clock className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{appointment.time}</span>
        </div>
      </div>
    </div>
  );
  
  const renderBookingForm = () => {
    if (activeBookingTab === 'hospital') {
      return (
        <div>
          {bookingStep === 1 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Select Hospital</h3>
              
              <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
                <Search className="w-5 h-5" style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280'
                }} />
                <input
                  type="text"
                  placeholder="Search hospitals..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {filteredHospitals.map(hospital => (
                  <div
                    key={hospital.id}
                    onClick={() => {
                      setSelectedHospital(hospital);
                      setBookingStep(2);
                    }}
                    style={{
                      padding: '1rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: 'white'
                    }}
                  >
                    <div style={{ fontWeight: '600' }}>{hospital.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{hospital.location}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {bookingStep === 2 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <button
                  onClick={() => setBookingStep(1)}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#6b7280'
                  }}
                >
                  ← Back
                </button>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>Select Doctor at {selectedHospital.name}</h3>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {hospitalDoctors.map(doctor => (
                  <div
                    key={doctor.id}
                    onClick={() => {
                      setSelectedDoctor(doctor);
                      setBookingStep(3);
                    }}
                    style={{
                      padding: '1rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: 'white'
                    }}
                  >
                    <div style={{ fontWeight: '600' }}>{doctor.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#3b82f6' }}>{doctor.specialty}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {bookingStep === 3 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <button
                  onClick={() => setBookingStep(2)}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#6b7280'
                  }}
                >
                  ← Back
                </button>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>Select Time for {selectedDoctor.name}</h3>
              </div>
              
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: '0.75rem',
                marginBottom: '1.5rem'
              }}>
                {timeSlots.map((time, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedTime(time)}
                    style={{
                      padding: '0.75rem',
                      textAlign: 'center',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: selectedTime === time ? '#dbeafe' : 'white'
                    }}
                  >
                    {time}
                  </div>
                ))}
              </div>
              
              <button
                onClick={handleBookAppointment}
                disabled={!selectedTime}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: selectedTime ? '#3b82f6' : '#e5e7eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: selectedTime ? 'pointer' : 'not-allowed'
                }}
              >
                Confirm Appointment
              </button>
            </div>
          )}
        </div>
      );
    } else if (activeBookingTab === 'doctor') {
      return (
        <div>
          {bookingStep === 1 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Find a Doctor</h3>
              
              <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
                <Search className="w-5 h-5" style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280'
                }} />
                <input
                  type="text"
                  placeholder="Search doctors by name or specialty..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {filteredDoctors.map(doctor => (
                  <div
                    key={doctor.id}
                    onClick={() => {
                      setSelectedDoctor(doctor);
                      setBookingStep(2);
                    }}
                    style={{
                      padding: '1rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: 'white'
                    }}
                  >
                    <div style={{ fontWeight: '600' }}>{doctor.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#3b82f6', marginBottom: '0.25rem' }}>{doctor.specialty}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{doctor.hospital}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {bookingStep === 2 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <button
                  onClick={() => setBookingStep(1)}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#6b7280'
                  }}
                >
                  ← Back
                </button>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>Select Time for {selectedDoctor.name}</h3>
              </div>
              
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: '0.75rem',
                marginBottom: '1.5rem'
              }}>
                {timeSlots.map((time, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedTime(time)}
                    style={{
                      padding: '0.75rem',
                      textAlign: 'center',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: selectedTime === time ? '#dbeafe' : 'white'
                    }}
                  >
                    {time}
                  </div>
                ))}
              </div>
              
              <button
                onClick={handleBookAppointment}
                disabled={!selectedTime}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: selectedTime ? '#3b82f6' : '#e5e7eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: selectedTime ? 'pointer' : 'not-allowed'
                }}
              >
                Confirm Appointment
              </button>
            </div>
          )}
        </div>
      );
    } else if (activeBookingTab === 'pharmacy') {
      return (
        <div>
          {bookingStep === 1 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Select Pharmacy</h3>
              
              <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
                <Search className="w-5 h-5" style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280'
                }} />
                <input
                  type="text"
                  placeholder="Search pharmacies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {filteredPharmacies.map(pharmacy => (
                  <div
                    key={pharmacy.id}
                    onClick={() => {
                      setSelectedPharmacy(pharmacy);
                      setBookingStep(2);
                      setSearchTerm('');
                    }}
                    style={{
                      padding: '1rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: 'white'
                    }}
                  >
                    <div style={{ fontWeight: '600' }}>{pharmacy.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{pharmacy.location}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {bookingStep === 2 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <button
                  onClick={() => {
                    setBookingStep(1);
                    setSearchTerm('');
                  }}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#6b7280'
                  }}
                >
                  ← Back
                </button>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>Select Medicines at {selectedPharmacy.name}</h3>
              </div>
              
              <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
                <Search className="w-5 h-5" style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280'
                }} />
                <input
                  type="text"
                  placeholder="Search medicines..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
                {filteredMedicines.map(medicine => {
                  const isSelected = selectedMedicines.some(m => m.id === medicine.id);
                  return (
                    <div
                      key={medicine.id}
                      onClick={() => toggleMedicineSelection(medicine)}
                      style={{
                        padding: '1rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '0.5rem',
                        cursor: 'pointer',
                        backgroundColor: isSelected ? '#dbeafe' : 'white'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: '600' }}>{medicine.name}</div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{medicine.type} - {medicine.price}</div>
                        </div>
                        
                        {isSelected && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                updateMedicineQuantity(medicine.id, -1);
                              }}
                              style={{
                                width: '24px',
                                height: '24px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                border: '1px solid #d1d5db',
                                borderRadius: '4px',
                                backgroundColor: 'white',
                                cursor: 'pointer'
                              }}
                            >
                              <Minus size={14} />
                            </button>
                            
                            <span style={{ minWidth: '30px', textAlign: 'center' }}>
                              {medicineQuantities[medicine.id] || 1}
                            </span>
                            
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                updateMedicineQuantity(medicine.id, 1);
                              }}
                              style={{
                                width: '24px',
                                height: '24px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                border: '1px solid #d1d5db',
                                borderRadius: '4px',
                                backgroundColor: 'white',
                                cursor: 'pointer'
                              }}
                            >
                              <Plus size={14} />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {selectedMedicines.length > 0 && (
                <div style={{ 
                  marginBottom: '1.5rem',
                  padding: '1rem',
                  backgroundColor: '#f9fafb',
                  borderRadius: '0.5rem',
                  border: '1px solid #e5e7eb'
                }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>Selected Medicines</h4>
                  
                  {selectedMedicines.map(medicine => (
                    <div 
                      key={medicine.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.5rem',
                        padding: '0.5rem',
                        borderBottom: '1px solid #e5e7eb'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: '500' }}>{medicine.name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                          {medicine.price} x {medicineQuantities[medicine.id] || 1}
                        </div>
                      </div>
                      
                      <button
                        onClick={() => toggleMedicineSelection(medicine)}
                        style={{
                          backgroundColor: 'transparent',
                          border: 'none',
                          color: '#ef4444',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <Trash size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={handleBookAppointment}
                disabled={selectedMedicines.length === 0}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: selectedMedicines.length > 0 ? '#3b82f6' : '#e5e7eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: selectedMedicines.length > 0 ? 'pointer' : 'not-allowed'
                }}
              >
                Order Medicines
              </button>
            </div>
          )}
        </div>
      );
    } else if (activeBookingTab === 'lab') {
      return (
        <div>
          {bookingStep === 1 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Select Lab</h3>
              
              <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
                <Search className="w-5 h-5" style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280'
                }} />
                <input
                  type="text"
                  placeholder="Search labs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {filteredLabs.map(lab => (
                  <div
                    key={lab.id}
                    onClick={() => {
                      setSelectedLab(lab);
                      setBookingStep(2);
                      setSearchTerm('');
                    }}
                    style={{
                      padding: '1rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      backgroundColor: 'white'
                    }}
                  >
                    <div style={{ fontWeight: '600' }}>{lab.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{lab.location}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {bookingStep === 2 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <button
                  onClick={() => {
                    setBookingStep(1);
                    setSearchTerm('');
                  }}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#6b7280'
                  }}
                >
                  ← Back
                </button>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>Select Tests at {selectedLab.name}</h3>
              </div>
              
              <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
                <Search className="w-5 h-5" style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280'
                }} />
                <input
                  type="text"
                  placeholder="Search tests..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
                {filteredLabTests.map(test => {
                  const isSelected = selectedTests.some(t => t.id === test.id);
                  return (
                    <div
                      key={test.id}
                      onClick={() => toggleTestSelection(test)}
                      style={{
                        padding: '1rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '0.5rem',
                        cursor: 'pointer',
                        backgroundColor: isSelected ? '#dbeafe' : 'white'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: '600' }}>{test.name}</div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{test.price}</div>
                        </div>
                        
                        {isSelected && (
                          <div style={{ 
                            width: '20px', 
                            height: '20px', 
                            borderRadius: '50%', 
                            backgroundColor: '#3b82f6',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            ✓
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {selectedTests.length > 0 && (
                <div style={{ 
                  marginBottom: '1.5rem',
                  padding: '1rem',
                  backgroundColor: '#f9fafb',
                  borderRadius: '0.5rem',
                  border: '1px solid #e5e7eb'
                }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>Selected Tests</h4>
                  
                  {selectedTests.map(test => (
                    <div 
                      key={test.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.5rem',
                        padding: '0.5rem',
                        borderBottom: '1px solid #e5e7eb'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: '500' }}>{test.name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{test.price}</div>
                      </div>
                      
                      <button
                        onClick={() => toggleTestSelection(test)}
                        style={{
                          backgroundColor: 'transparent',
                          border: 'none',
                          color: '#ef4444',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <Trash size={16} />
                      </button>
                    </div>
                  ))}
                  
                  <div style={{ 
                    marginTop: '1rem', 
                    paddingTop: '0.5rem', 
                    borderTop: '1px solid #e5e7eb',
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontWeight: '600'
                  }}>
                    <span>Total</span>
                    <span>
                      ₹{selectedTests.reduce((sum, test) => {
                        const price = parseInt(test.price.replace('₹', ''));
                        return sum + price;
                      }, 0)}
                    </span>
                  </div>
                </div>
              )}
              
              {selectedTests.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' }}>Select Time</h3>
                  
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(3, 1fr)', 
                    gap: '0.75rem',
                    marginBottom: '1.5rem'
                  }}>
                    {timeSlots.map((time, index) => (
                      <div
                        key={index}
                        onClick={() => setSelectedTime(time)}
                        style={{
                          padding: '0.75rem',
                          textAlign: 'center',
                          border: '1px solid #d1d5db',
                          borderRadius: '0.5rem',
                          cursor: 'pointer',
                          backgroundColor: selectedTime === time ? '#dbeafe' : 'white'
                        }}
                      >
                        {time}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <button
                onClick={handleBookAppointment}
                disabled={selectedTests.length === 0 || !selectedTime}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: (selectedTests.length > 0 && selectedTime) ? '#3b82f6' : '#e5e7eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: (selectedTests.length > 0 && selectedTime) ? 'pointer' : 'not-allowed'
                }}
              >
                Book Tests
              </button>
            </div>
          )}
        </div>
      );
    }
  };
  
  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        <Header userData={userData} />
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » Appointments
          </div>
          
          {/* Appointments Sub-menu */}
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            marginBottom: '1.5rem',
            borderBottom: '1px solid #e5e7eb',
            paddingBottom: '0.5rem'
          }}>
            <button
              onClick={() => {
                setShowBookingForm(true);
                setActiveTab('book');
                resetBookingState();
              }}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: activeTab === 'book' ? '#3b82f6' : 'transparent',
                color: activeTab === 'book' ? 'white' : '#6b7280',
                border: 'none',
                borderRadius: '0.5rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Book
            </button>
            
            <button
              onClick={() => {
                setShowBookingForm(false);
                setActiveTab('upcoming');
              }}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: activeTab === 'upcoming' ? '#3b82f6' : 'transparent',
                color: activeTab === 'upcoming' ? 'white' : '#6b7280',
                border: 'none',
                borderRadius: '0.5rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Upcoming
            </button>
            
            <button
              onClick={() => {
                setShowBookingForm(false);
                setActiveTab('previous');
              }}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: activeTab === 'previous' ? '#3b82f6' : 'transparent',
                color: activeTab === 'previous' ? 'white' : '#6b7280',
                border: 'none',
                borderRadius: '0.5rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Previous
            </button>
          </div>
          
          {/* Booking Form */}
          {showBookingForm && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              marginBottom: '1.5rem'
            }}>
              <div style={{ 
                display: 'flex', 
                gap: '1rem', 
                marginBottom: '1.5rem',
                borderBottom: '1px solid #e5e7eb',
                paddingBottom: '0.5rem'
              }}>
                <button
                  onClick={() => {
                    setActiveBookingTab('hospital');
                    resetBookingState();
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: activeBookingTab === 'hospital' ? '#3b82f6' : 'transparent',
                    color: activeBookingTab === 'hospital' ? 'white' : '#6b7280',
                    border: 'none',
                    borderRadius: '0.5rem',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Hospital
                </button>
                
                <button
                  onClick={() => {
                    setActiveBookingTab('doctor');
                    resetBookingState();
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: activeBookingTab === 'doctor' ? '#3b82f6' : 'transparent',
                    color: activeBookingTab === 'doctor' ? 'white' : '#6b7280',
                    border: 'none',
                    borderRadius: '0.5rem',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Doctor
                </button>
                
                <button
                  onClick={() => {
                    setActiveBookingTab('pharmacy');
                    resetBookingState();
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: activeBookingTab === 'pharmacy' ? '#3b82f6' : 'transparent',
                    color: activeBookingTab === 'pharmacy' ? 'white' : '#6b7280',
                    border: 'none',
                    borderRadius: '0.5rem',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Pharmacy
                </button>
                
                <button
                  onClick={() => {
                    setActiveBookingTab('lab');
                    resetBookingState();
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: activeBookingTab === 'lab' ? '#3b82f6' : 'transparent',
                    color: activeBookingTab === 'lab' ? 'white' : '#6b7280',
                    border: 'none',
                    borderRadius: '0.5rem',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Lab
                </button>
              </div>
              
              {renderBookingForm()}
            </div>
          )}
          
          {/* Upcoming Appointments */}
          {activeTab === 'upcoming' && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              marginBottom: '1.5rem'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Upcoming Appointments</h2>
              
              {upcomingAppointments.length > 0 ? (
                upcomingAppointments.map(appointment => renderAppointmentCard(appointment))
              ) : (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                  No upcoming appointments
                </div>
              )}
            </div>
          )}
          
          {/* Previous Appointments */}
          {activeTab === 'previous' && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '2rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Previous Appointments</h2>
              
              {previousAppointments.length > 0 ? (
                previousAppointments.map(appointment => renderAppointmentCard(appointment))
              ) : (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                  No previous appointments
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AppointmentsPageUpdated;