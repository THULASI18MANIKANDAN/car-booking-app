# Car Booking Web Application

A comprehensive car booking system built with Python Flask and SQLite, featuring user authentication, role-based access control, and a modern responsive design.

## Features

### User Features
- **User Registration & Login**: Secure authentication system with password hashing
- **Car Browsing**: View available cars with detailed information and images
- **Car Booking**: Book cars with date selection and price calculation
- **Payment Simulation**: Integrated Razorpay payment simulation
- **Booking Management**: View and cancel personal bookings
- **Responsive Design**: Modern UI with animations and mobile-friendly layout

### Admin Features
- **Admin Dashboard**: Comprehensive overview with statistics
- **User Management**: View all registered users and their roles
- **Car Management**: Add, edit, and manage car inventory
- **Booking Management**: View all bookings across the system
- **Status Tracking**: Monitor car availability and rental status

### Technical Features
- **Role-Based Access Control**: Separate user and admin functionalities
- **Session Management**: Secure session handling with proper authentication
- **Flash Messages**: Real-time feedback for user actions
- **Image Support**: Car image management with URL-based storage
- **Database Integration**: SQLite database with proper relationships
- **Modern CSS**: Gradient designs, animations, and responsive layout

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Run the application**:
   \`\`\`bash
   python app.py
   \`\`\`

4. **Access the application**:
   - Open your browser and go to `http://localhost:5000`
   - The database will be automatically created on first run

## Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123

### Test User Account
You can register a new user account through the registration page.

## Project Structure

\`\`\`
car-booking-app/
├── app.py                 # Main Flask application
├── car_booking.db         # SQLite database (created automatically)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── cars.html         # Car listing page
│   ├── car_detail.html   # Individual car details
│   ├── book_car.html     # Car booking form
│   ├── payment.html      # Payment simulation
│   ├── my_bookings.html  # User's bookings
│   ├── admin_dashboard.html  # Admin dashboard
│   ├── admin_users.html      # User management
│   ├── admin_cars.html       # Car management
│   ├── admin_bookings.html   # Booking management
│   ├── add_car.html          # Add new car
│   └── edit_car.html         # Edit car details
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── script.js     # JavaScript functionality
│   └── uploads/          # File upload directory
└── scripts/
    └── init_database.sql # Database initialization script
\`\`\`

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: User email address
- `password`: Hashed password
- `role`: User role (user/admin)
- `created_at`: Registration timestamp

### Cars Table
- `id`: Primary key
- `name`: Car name/title
- `brand`: Car manufacturer
- `model`: Car model
- `year`: Manufacturing year
- `price_per_day`: Daily rental price
- `image_url`: Car image URL
- `status`: Availability status (available/rented/maintenance)
- `description`: Car description
- `created_at`: Creation timestamp

### Bookings Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `car_id`: Foreign key to cars table
- `start_date`: Booking start date
- `end_date`: Booking end date
- `total_amount`: Total booking cost
- `payment_id`: Simulated payment ID
- `status`: Booking status (confirmed/cancelled)
- `created_at`: Booking timestamp

## Key Features Explained

### Authentication System
- Passwords are hashed using SHA-256
- Session-based authentication with role checking
- Protected routes with decorators

### Payment Simulation
- Simulates Razorpay payment gateway
- Generates unique payment IDs
- Redirects after successful "payment"

### Admin Dashboard
- Real-time statistics display
- Quick access to management functions
- Recent bookings overview

### Responsive Design
- Mobile-first approach
- CSS Grid and Flexbox layouts
- Smooth animations and transitions
- Modern gradient designs

## Usage Guide

### For Users
1. Register a new account or login
2. Browse available cars on the Cars page
3. Click on a car to view details
4. Click "Book Now" to start booking process
5. Select dates and proceed to payment
6. Complete the simulated payment
7. View your bookings in "My Bookings"
8. Cancel bookings if needed

### For Admins
1. Login with admin credentials
2. Access the Admin Dashboard
3. Manage users, cars, and bookings
4. Add new cars with images and details
5. Edit existing car information
6. Monitor booking status and statistics

## Customization

### Adding New Car Images
- Use the image URL field when adding/editing cars
- Recommended image size: 500x300 pixels
- Supported formats: JPG, PNG, WebP

### Modifying Styles
- Edit `static/css/style.css` for styling changes
- The CSS uses CSS custom properties for easy theming
- Responsive breakpoints are included

### Database Modifications
- Modify the database schema in `app.py`
- Update the initialization script in `scripts/init_database.sql`
- Remember to handle migrations for existing data

## Security Features

- Password hashing with SHA-256
- Session-based authentication
- CSRF protection through Flask's built-in features
- Role-based access control
- Input validation and sanitization

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Common Issues

1. **Database not created**: Ensure write permissions in the project directory
2. **Images not loading**: Check image URLs and internet connection
3. **Styles not applying**: Clear browser cache and refresh
4. **Login issues**: Verify username/password and check database

### Development Tips

- Use Flask's debug mode for development: `app.run(debug=True)`
- Check the browser console for JavaScript errors
- Monitor the Flask console for server-side errors
- Use browser developer tools for responsive testing

## Future Enhancements

Potential improvements for the application:

- Real payment gateway integration
- Email notifications for bookings
- Car search and filtering
- User profile management
- Booking history and receipts
- Car reviews and ratings
- Multi-language support
- API endpoints for mobile apps

## License

This project is created for educational purposes. Feel free to modify and use as needed.

## Support

For issues or questions about this application, please check the code comments and documentation. The application is designed to be self-contained and easy to understand.
