import React, { useState } from 'react';
import { Search, Star } from 'lucide-react';

const DoctorReviewsSection = () => {
  const [reviewSearchTerm, setReviewSearchTerm] = useState('');
  
  const allReviews = [
    { id: 1, patient: 'John D.', doctor: 'Dr. Rajesh Kumar', rating: 5, comment: 'Excellent doctor, very professional and caring.', date: '2024-01-10' },
    { id: 2, patient: 'Sarah M.', doctor: 'Dr. Priya Sharma', rating: 4, comment: 'Great experience with pediatric care for my child.', date: '2024-01-08' },
    { id: 3, patient: 'Mike R.', doctor: 'Dr. Amit Patel', rating: 5, comment: 'Very knowledgeable neurologist, highly recommend.', date: '2024-01-05' },
    { id: 4, patient: 'Lisa K.', doctor: 'Dr. Sunita Reddy', rating: 4, comment: 'Professional and understanding gynecologist.', date: '2024-01-03' },
    { id: 5, patient: 'Thomas B.', doctor: 'Dr. Rajesh Kumar', rating: 5, comment: 'Excellent bedside manner and very thorough examination.', date: '2024-01-01' },
    { id: 6, patient: 'Emma W.', doctor: 'Dr. Vikram Singh', rating: 5, comment: 'Best cardiologist in the city. Very detailed explanations.', date: '2023-12-29' },
    { id: 7, patient: 'Robert J.', doctor: 'Dr. Priya Sharma', rating: 4, comment: 'My son loves her. Very patient with children.', date: '2023-12-27' }
  ];

  const filteredReviews = reviewSearchTerm.trim() === '' 
    ? allReviews.slice(0, 4) 
    : allReviews.filter(review => 
        review.doctor.toLowerCase().includes(reviewSearchTerm.toLowerCase())
      );

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '1rem',
      padding: '2rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>Patient Reviews</h3>
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
            placeholder="Search by doctor name..."
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
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>visited {review.doctor}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className={`w-4 h-4 ${i < review.rating ? 'text-yellow-500' : 'text-gray-300'}`} />
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

export default DoctorReviewsSection;