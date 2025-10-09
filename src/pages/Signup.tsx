import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

export default function Signup() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      className="min-h-screen"
    >
      <div className="container mx-auto px-6 py-24">
        <Link to="/">
          <Button className="btn-secondary mb-8 rounded-xl">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </Link>
        
        <div className="max-w-md mx-auto">
          <h1 className="text-5xl font-bold gradient-text mb-6 text-center">Sign Up</h1>
          <p className="text-xl text-gray-400 mb-12 text-center">
            Get started with QuantFin AI today
          </p>
          
          <div className="card">
            <p className="text-gray-400 text-center mb-6">
              Authentication system coming soon. We're building a secure signup experience for you.
            </p>
            
            <div className="text-center">
              <Link to="/dashboard">
                <Button className="btn-primary rounded-xl">
                  View Demo Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
