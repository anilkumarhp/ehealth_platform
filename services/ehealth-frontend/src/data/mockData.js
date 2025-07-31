const mockData = {
  hospitals: {
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
    },
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

export default mockData;