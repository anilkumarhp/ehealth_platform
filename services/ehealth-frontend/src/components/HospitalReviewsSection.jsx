import React, { useState } from 'react';
import { Search } from 'lucide-react';

const HospitalReviewsSection = () => {
  const [reviewSearchTerm, setReviewSearchTerm] = useState('');
  
  const allReviews = [
    { id: 1, patient: 'Alex R.', hospital: 'Apollo Hospital', rating: 5, comment: 'Excellent facilities and professional staff. Highly recommended.', date: '2024-01-12' },
    { id: 2, patient: 'Maria S.', hospital: 'Fortis Hospital', rating: 4, comment: 'Good service and clean environment. Quick appointment scheduling.', date: '2024-01-10' },
    { id: 3, patient: 'David K.', hospital: 'Max Super Speciality Hospital', rating: 5, comment: 'Outstanding cardiac care unit. Saved my life with their expertise.', date: '2024-01-08' },
    { id: 4, patient: 'Jennifer L.', hospital: 'AIIMS Delhi', rating: 4, comment: 'Great doctors and affordable treatment. Long wait times though.', date: '2024-01-06' },
    { id: 5, patient: 'Robert M.', hospital: 'Apollo Hospital', rating: 5, comment: 'Excellent emergency care. The staff was very attentive.', date: '2024-01-04' },
    { id: 6, patient: 'Emily T.', hospital: 'Manipal Hospital', rating: 3, comment: 'Good doctors but the waiting time was too long.', date: '2024-01-02' },
    { id: 7, patient: 'Michael P.', hospital: 'Fortis Hospital', rating: 4, comment: 'Clean facilities and professional staff. Would recommend.', date: '2023-12-28' }
  ];

  const filteredReviews = reviewSearchTerm.trim() === '' 
    ? allReviews.slice(0, 4) 
    : allReviews.filter(review => 
        review.hospital.toLowerCase().includes(reviewSearchTerm.toLowerCase())
      );

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '1rem',
      padding: '2rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>Hospital Reviews</h3>
        <div style={{ position: 'relative', width: '250px' }}>
          <Search className="w-4 h-4" style={{
            position: 'absolute',
            left: '0.75rem',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#6b7280'
          }} />
          <input
            type="text"
            placeholder="Search by hospital name..."
            value={reviewSearchTerm}
            onChange={(e) => setReviewSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 0.5rem 0.5rem 2rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '0.875rem'
            }}
          />
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filteredReviews.map((review) => (
          <div key={review.id} style={{
            padding: '1rem',
            backgroundColor: '#f8fafc',
            borderRadius: '0.5rem',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
              <div>
                <div style={{ fontWeight: '600', color: '#111827', fontSize: '0.875rem' }}>{review.patient}</div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>visited {review.hospital}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                {[...Array(5)].map((_, i) => (
                  <span key={i} style={{ color: i < review.rating ? '#fbbf24' : '#d1d5db' }}>★</span>
                ))}
              </div>
            </div>
            <p style={{ fontSize: '0.875rem', color: '#374151', marginBottom: '0.5rem' }}>{review.comment}</p>
            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{new Date(review.date).toLocaleDateString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HospitalReviewsSection;