import { motion } from 'framer-motion';
import { ArrowLeft, Mail, MapPin, Phone } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

export default function Contact() {
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
        
        <h1 className="text-5xl font-bold gradient-text mb-6">Contact Us</h1>
        <p className="text-xl text-gray-400 max-w-3xl mb-12">
          Get in touch with our team. We're here to help you with your portfolio management needs.
        </p>
        
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl">
          <div className="card text-center">
            <Mail className="w-8 h-8 text-blue-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">Email</h3>
            <p className="text-gray-400 text-sm">contact@quantfin.ai</p>
          </div>
          
          <div className="card text-center">
            <Phone className="w-8 h-8 text-purple-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">Phone</h3>
            <p className="text-gray-400 text-sm">+91 XXXX-XXXXXX</p>
          </div>
          
          <div className="card text-center">
            <MapPin className="w-8 h-8 text-emerald-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">Location</h3>
            <p className="text-gray-400 text-sm">Mumbai, India</p>
          </div>
        </div>
        
        <div className="mt-12 card max-w-4xl">
          <p className="text-gray-400">
            Contact form coming soon. For now, reach out to us via email.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
