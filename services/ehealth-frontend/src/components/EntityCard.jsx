import { Link } from 'react-router-dom';
import { 
  Hospital, 
  Pill, 
  FlaskConical, 
  User,
  MapPin,
  Phone,
  Star,
  Calendar,
  ShoppingBag
} from 'lucide-react';

// Generic card component that can be used for hospitals, doctors, pharmacies, and labs
export const EntityCard = ({ entity, type }) => {
  // Determine icon based on entity type
  const getIcon = () => {
    switch(type) {
      case 'hospitals':
        return <Hospital className="w-5 h-5 text-blue-600" />;
      case 'doctors':
        return <User className="w-5 h-5 text-blue-600" />;
      case 'pharmacies':
        return <Pill className="w-5 h-5 text-blue-600" />;
      case 'labs':
        return <FlaskConical className="w-5 h-5 text-blue-600" />;
      default:
        return <Hospital className="w-5 h-5 text-blue-600" />;
    }
  };

  // Determine button text based on entity type
  const getButtonText = () => {
    switch(type) {
      case 'hospitals':
      case 'doctors':
        return 'Book Appointment';
      case 'pharmacies':
        return 'Order';
      case 'labs':
        return 'Book Test';
      default:
        return 'Book';
    }
  };

  // Determine button icon based on entity type
  const getButtonIcon = () => {
    switch(type) {
      case 'hospitals':
      case 'doctors':
      case 'labs':
        return <Calendar className="w-4 h-4" />;
      case 'pharmacies':
        return <ShoppingBag className="w-4 h-4" />;
      default:
        return <Calendar className="w-4 h-4" />;
    }
  };

  // Map entity type to booking tab
  const getBookingTab = () => {
    switch(type) {
      case 'hospitals':
        return 'hospital';
      case 'doctors':
        return 'doctor';
      case 'pharmacies':
        return 'pharmacy';
      case 'labs':
        return 'lab';
      default:
        return 'hospital';
    }
  };

  const handleBookingClick = (e) => {
    e.preventDefault(); // Prevent navigation from Link
    console.log('Booking button clicked for:', entity.name);
    
    // Store entity data in sessionStorage to pass to appointments page
    sessionStorage.setItem('selectedEntityType', getBookingTab());
    sessionStorage.setItem('selectedEntityData', JSON.stringify(entity));
    
    // Navigate to appointments page
    window.location.href = '/appointments';
  };

  return (
    <Link to={`/${type}/${entity.id || 1}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <div style={{
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              {getIcon()}
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                {entity.name}
              </h3>
              {entity.openNow !== undefined && (
                <span style={{
                  fontSize: '0.75rem',
                  backgroundColor: entity.openNow ? '#dcfce7' : '#fee2e2',
                  color: entity.openNow ? '#166534' : '#b91c1c',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '0.25rem',
                  marginLeft: '0.5rem'
                }}>
                  {entity.openNow ? 'Open Now' : 'Closed'}
                </span>
              )}
            </div>
            
            {entity.address && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
                <MapPin className="w-4 h-4 text-gray-500" />
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{entity.address}</span>
              </div>
            )}
            
            {entity.specialty && (
              <div style={{ fontSize: '0.875rem', color: '#3b82f6', fontWeight: '500', marginBottom: '0.5rem' }}>
                {entity.specialty}
              </div>
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
              {entity.phone && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Phone className="w-4 h-4 text-gray-500" />
                  <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{entity.phone}</span>
                </div>
              )}
              
              {entity.rating && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span style={{ fontWeight: '600', color: '#111827' }}>{entity.rating}</span>
                </div>
              )}
            </div>
            
            {entity.distance && (
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                <strong>Distance:</strong> {entity.distance}
              </div>
            )}
            
            {entity.specialties && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                {entity.specialties.slice(0, 3).map((specialty, index) => (
                  <span key={index} style={{
                    fontSize: '0.75rem',
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '0.25rem'
                  }}>
                    {specialty}
                  </span>
                ))}
              </div>
            )}
            
            {entity.qualifications && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                {entity.qualifications.slice(0, 3).map((qual, index) => (
                  <span key={index} style={{
                    fontSize: '0.75rem',
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '0.25rem'
                  }}>
                    {qual}
                  </span>
                ))}
              </div>
            )}
          </div>
          
          <button 
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: type === 'pharmacies' ? '#10b981' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginLeft: '1rem'
            }}
            onClick={handleBookingClick}
          >
            {getButtonIcon()}
            {getButtonText()}
          </button>
        </div>
      </div>
    </Link>
  );
};

export default EntityCard;