import { useState } from 'react';
import { 
  Search
} from 'lucide-react';
import { EntityCard } from '../components/EntityCard';
import PharmacyAdsSection from '../components/PharmacyAdsSection';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

const PharmacyPage = () => {
  const [activeMenu, setActiveMenu] = useState('pharmacy');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Mock data for recent pharmacy purchases
  const recentPurchases = [
    {
      id: 1,
      name: 'MedPlus Pharmacy',
      address: '123 Health Street, Downtown',
      phone: '+1 (555) 123-4567',
      date: '2024-01-10',
      items: ['Paracetamol', 'Vitamin C', 'Bandages'],
      total: 28.50
    },
    {
      id: 2,
      name: 'LifeCare Medicines',
      address: '456 Wellness Avenue, Midtown',
      phone: '+1 (555) 987-6543',
      date: '2024-01-05',
      items: ['Antibiotics', 'Cough Syrup'],
      total: 45.75
    },
    {
      id: 3,
      name: 'QuickMeds Pharmacy',
      address: '789 Care Road, Uptown',
      phone: '+1 (555) 456-7890',
      date: '2023-12-28',
      items: ['Blood Pressure Medication', 'Glucose Monitor'],
      total: 120.00
    }
  ];

  // Mock data for nearby pharmacies
  const allPharmacies = [
    {
      id: 4,
      name: 'Apollo Pharmacy',
      address: '21 Health Lane, Central District',
      phone: '+91 44 2829 3333',
      distance: '0.5 km',
      rating: 4.7,
      openNow: true
    },
    {
      id: 5,
      name: 'MedPlus Pharmacy',
      address: 'Sector 62, Phase VIII, North Area',
      phone: '+91 172 496 7000',
      distance: '1.2 km',
      rating: 4.5,
      openNow: true
    },
    {
      id: 6,
      name: 'Wellness Forever',
      address: '1 Press Enclave Road, South District',
      phone: '+91 11 2651 5050',
      distance: '2.3 km',
      rating: 4.6,
      openNow: false
    },
    {
      id: 7,
      name: 'Medikart Pharmacy',
      address: '98 Rustom Bagh, East District',
      phone: '+91 80 2502 4444',
      distance: '3.1 km',
      rating: 4.4,
      openNow: true
    },
    {
      id: 8,
      name: 'HealthMart',
      address: 'Sri Aurobindo Marg, West District',
      phone: '+91 11 2658 8500',
      distance: '3.8 km',
      rating: 4.8,
      openNow: false
    }
  ];

  const handleSearch = (term) => {
    if (term.trim() === '') {
      setSearchResults([]);
    } else {
      const filtered = allPharmacies.filter(pharmacy =>
        pharmacy.name.toLowerCase().includes(term.toLowerCase()) ||
        pharmacy.address.toLowerCase().includes(term.toLowerCase())
      );
      setSearchResults(filtered);
    }
  };

  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        <Header userData={userData} />
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » Pharmacy
          </div>
          
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}>
            <div style={{ marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                Find Pharmacies
              </h2>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Search for pharmacies by name or location
              </p>
            </div>
            <div style={{ position: 'relative', width: '100%', maxWidth: '600px' }}>
              <Search className="w-5 h-5" style={{
                position: 'absolute',
                left: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#6b7280'
              }} />
              <input
                type="text"
                placeholder="Search pharmacies by name or location..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  handleSearch(e.target.value);
                }}
                style={{
                  width: '100%',
                  padding: '1rem 1rem 1rem 3rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '0.75rem',
                  fontSize: '1rem',
                  transition: 'all 0.2s',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#3b82f6';
                  e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e5e7eb';
                  e.target.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
                }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              }}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                    Recent Purchases
                  </h2>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {recentPurchases.map((purchase) => (
                    <EntityCard key={purchase.id} entity={purchase} type="pharmacies" />
                  ))}
                </div>
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              }}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                    {searchResults.length > 0 ? 'Search Results' : 'Nearby Pharmacies'}
                  </h2>
                  {searchResults.length > 0 && (
                    <div style={{
                      display: 'inline-block',
                      backgroundColor: '#dbeafe',
                      color: '#1e40af',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '1rem',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}>
                      {searchResults.length} pharmacy{searchResults.length !== 1 ? 'ies' : ''} found
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {(searchResults.length > 0 ? searchResults : allPharmacies).map((pharmacy) => (
                    <EntityCard key={pharmacy.id} entity={pharmacy} type="pharmacies" />
                  ))}
                </div>
              </div>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'sticky', top: '1.5rem', alignSelf: 'flex-start' }}>
              <PharmacyAdsSection />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default PharmacyPage;