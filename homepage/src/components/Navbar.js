import React from 'react';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">INTERNSHIPS.</div>
      {/* Navigation links - update href attributes when implementing routing */}
      <ul className="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/leetcode">LeetCode Tracker</a></li>
        <li><a href="/behavioral">Behavioral Interview</a></li>
        <li><a href="/internships">Internship Board</a></li>
        <li><a href="/signup">Sign Up</a></li>
      </ul>
    </nav>
  );
}

export default Navbar;