import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { SignUp } from '@/lib/clerk';
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
          
          <div className="flex justify-center">
            <SignUp 
              appearance={{
                elements: {
                  formButtonPrimary: 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600',
                  card: 'bg-gray-900/50 backdrop-blur-xl border border-white/10',
                  headerTitle: 'text-white',
                  headerSubtitle: 'text-gray-400',
                  socialButtonsBlockButton: 'bg-white/5 border-white/10 text-white hover:bg-white/10',
                  formFieldLabel: 'text-gray-300',
                  formFieldInput: 'bg-white/5 border-white/10 text-white',
                  footerActionLink: 'text-blue-400 hover:text-blue-300',
                }
              }}
              routing="path"
              path="/signup"
              signInUrl="/signin"
              afterSignUpUrl="/dashboard"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
