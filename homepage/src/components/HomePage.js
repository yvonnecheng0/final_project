import React from 'react';
import './HomePage.css';
import Navbar from './Navbar';

function HomePage() {
  return (
    <div className="home-page">
      <Navbar />
      {/* Video background for landing page */}
      <video autoPlay loop muted playsInline className="background-video">
        <source src="/seoBackgroundVideo.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      {/* Overlay to improve text visibility over video */}
      <div className="overlay"></div>
      {/* Main content with smooth fade-in transition */}
      <div className="content" style={{transition: 'opacity 0.5s ease-in-out'}}>
        <h1>Internship Tracker</h1>
        <p>Discover Top 1% Opportunities Worldwide</p>
        {/* Search functionality - to be implemented */}
        <div className="search-bar">
          <input type="text" placeholder="Search for internships..." />
          <button>Search</button>
        </div>
      </div>
    </div>
  );
}

export default HomePage;