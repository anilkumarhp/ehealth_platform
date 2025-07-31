import { Link } from 'react-router-dom';

const RegistrationPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-inter flex flex-col">
      {/* Navigation Bar */}
      <header className="w-full px-8 py-4 border-b border-gray-700">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="text-xl font-bold text-white">
            Ehealth Platform
          </div>
          
          {/* Login Link */}
          <Link 
            to="/login" 
            className="text-gray-200 hover:text-white transition-colors"
          >
            Login
          </Link>
        </div>
      </header>

      {/* Main Content - Centered Vertically and Horizontally */}
      <main className="flex-1 flex items-center justify-center p-8">
        <div className="flex gap-8 max-w-6xl w-full">
          
          {/* Left Column - Image (wider) */}
          <div className="w-2/3">
            <div className="border-dashed border-2 border-gray-600 rounded-lg p-4">
              <img 
                src="https://placehold.co/900x600/111827/4b5563?text=Image"
                alt="Healthcare Platform"
                className="w-full h-auto rounded"
              />
            </div>
          </div>

          {/* Right Column - Registration Panel (narrower) */}
          <div className="w-1/3">
            <div className="border border-gray-700 rounded-lg p-8">
              <div className="space-y-6">
                
                {/* Heading */}
                <h1 className="text-center text-lg font-bold tracking-widest uppercase">
                  REGISTRATION
                </h1>

                {/* Logo Placeholder */}
                <div className="flex justify-center">
                  <div className="w-16 h-16 rounded-full border border-gray-600 flex items-center justify-center">
                    <span className="text-sm">Logo</span>
                  </div>
                </div>

                {/* Patient Button */}
                <button className="w-full py-3 px-4 border border-gray-600 rounded hover:bg-gray-800 transition-colors">
                  <Link to="/register/patient" className="block w-full h-full">
                    PATIENT
                  </Link>
                </button>

                {/* Organization Button */}
                <button className="w-full py-3 px-4 border border-gray-600 rounded hover:bg-gray-800 transition-colors">
                  <Link to="/register/organization" className="block w-full h-full">
                    ORGANIZATION
                  </Link>
                </button>

                {/* Description Text */}
                <p className="text-sm text-gray-400 text-center">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>

              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};

export default RegistrationPage;