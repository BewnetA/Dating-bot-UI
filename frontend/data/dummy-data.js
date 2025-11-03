// Enhanced dummy data with date ranges
const dummyData = {
    stats: {
        today: {
            totalUsers: 1250,
            activeUsers: 980,
            totalMatches: 3450,
            pendingPayments: 12
        },
        yesterday: {
            totalUsers: 1245,
            activeUsers: 975,
            totalMatches: 3420,
            pendingPayments: 10
        },
        last7: {
            totalUsers: 1250,
            activeUsers: 980,
            totalMatches: 3450,
            pendingPayments: 12
        },
        last30: {
            totalUsers: 1180,
            activeUsers: 920,
            totalMatches: 3150,
            pendingPayments: 8
        },
        last90: {
            totalUsers: 1050,
            activeUsers: 850,
            totalMatches: 2850,
            pendingPayments: 5
        },
        thisMonth: {
            totalUsers: 1220,
            activeUsers: 960,
            totalMatches: 3350,
            pendingPayments: 11
        },
        lastMonth: {
            totalUsers: 1150,
            activeUsers: 900,
            totalMatches: 3050,
            pendingPayments: 7
        },
        thisYear: {
            totalUsers: 1250,
            activeUsers: 980,
            totalMatches: 3450,
            pendingPayments: 12
        },
        previousPeriod: {
            today: {
                totalUsers: 1248,
                activeUsers: 978,
                totalMatches: 3440,
                pendingPayments: 11
            },
            yesterday: {
                totalUsers: 1240,
                activeUsers: 970,
                totalMatches: 3400,
                pendingPayments: 9
            },
            last7: {
                totalUsers: 1200,
                activeUsers: 940,
                totalMatches: 3200,
                pendingPayments: 8
            },
            last30: {
                totalUsers: 1100,
                activeUsers: 860,
                totalMatches: 2900,
                pendingPayments: 6
            },
            last90: {
                totalUsers: 950,
                activeUsers: 780,
                totalMatches: 2500,
                pendingPayments: 3
            },
            thisMonth: {
                totalUsers: 1180,
                activeUsers: 920,
                totalMatches: 3100,
                pendingPayments: 7
            },
            lastMonth: {
                totalUsers: 1080,
                activeUsers: 840,
                totalMatches: 2800,
                pendingPayments: 5
            },
            thisYear: {
                totalUsers: 1000,
                activeUsers: 800,
                totalMatches: 2500,
                pendingPayments: 4
            }
        }
    },
    users: [
        {
            user_id: 1001,
            username: "john_doe",
            first_name: "John",
            last_name: "Doe",
            gender: "male",
            city: "New York",
            coins: 150,
            is_active: true,
            created_at: "2023-10-01T10:30:00Z"
        },
        {
            user_id: 1002,
            username: "jane_smith",
            first_name: "Jane",
            last_name: "Smith",
            gender: "female",
            city: "Los Angeles",
            coins: 75,
            is_active: true,
            created_at: "2023-09-28T14:45:00Z"
        },
        {
            user_id: 1003,
            username: "mike_j",
            first_name: "Mike",
            last_name: "Johnson",
            gender: "male",
            city: "Chicago",
            coins: 200,
            is_active: false,
            created_at: "2023-09-25T09:15:00Z"
        },
        {
            user_id: 1004,
            username: "sarah_w",
            first_name: "Sarah",
            last_name: "Williams",
            gender: "female",
            city: "Miami",
            coins: 50,
            is_active: true,
            created_at: "2023-09-20T16:20:00Z"
        },
        {
            user_id: 1005,
            username: "alex_t",
            first_name: "Alex",
            last_name: "Taylor",
            gender: "other",
            city: "Seattle",
            coins: 120,
            is_active: true,
            created_at: "2023-09-15T11:10:00Z"
        }
    ],
    payments: [
        {
            _id: "pay001",
            user_id: 1001,
            first_name: "John",
            username: "john_doe",
            package_name: "Gold Package",
            coins_amount: 500,
            price: 49.99,
            status: "pending",
            screenshot_file_id: "file123",
            created_at: "2023-10-01T09:30:00Z"
        },
        {
            _id: "pay002",
            user_id: 1002,
            first_name: "Jane",
            username: "jane_smith",
            package_name: "Silver Package",
            coins_amount: 250,
            price: 24.99,
            status: "approved",
            screenshot_file_id: "file456",
            created_at: "2023-09-28T14:15:00Z"
        },
        {
            _id: "pay003",
            user_id: 1004,
            first_name: "Sarah",
            username: "sarah_w",
            package_name: "Bronze Package",
            coins_amount: 100,
            price: 9.99,
            status: "rejected",
            screenshot_file_id: "file789",
            created_at: "2023-09-25T11:45:00Z"
        },
        {
            _id: "pay004",
            user_id: 1005,
            first_name: "Alex",
            username: "alex_t",
            package_name: "Gold Package",
            coins_amount: 500,
            price: 49.99,
            status: "pending",
            screenshot_file_id: "file101",
            created_at: "2023-09-20T16:20:00Z"
        }
    ],
    complaints: [
        {
            _id: "comp001",
            user_id: 1001,
            complaint_type: "Inappropriate Behavior",
            complaint_text: "User was sending inappropriate messages",
            reported_user_id: 1003,
            status: "pending",
            created_at: "2023-09-30T12:30:00Z"
        },
        {
            _id: "comp002",
            user_id: 1002,
            complaint_type: "Fake Profile",
            complaint_text: "Profile pictures appear to be fake",
            reported_user_id: 1005,
            status: "resolved",
            created_at: "2023-09-25T15:45:00Z"
        },
        {
            _id: "comp003",
            user_id: 1004,
            complaint_type: "Harassment",
            complaint_text: "User is continuously messaging despite being asked to stop",
            reported_user_id: 1001,
            status: "pending",
            created_at: "2023-09-20T10:15:00Z"
        }
    ],
    charts: {
        genderDistribution: {
            all: [650, 550, 50],
            last7: [45, 38, 2],
            last30: [180, 150, 15]
        },
        registrations: {
            last7: {
                dates: ['Sep 25', 'Sep 26', 'Sep 27', 'Sep 28', 'Sep 29', 'Sep 30', 'Oct 1'],
                counts: [15, 22, 18, 25, 20, 28, 32]
            },
            last30: {
                dates: ['Sep 1', 'Sep 5', 'Sep 10', 'Sep 15', 'Sep 20', 'Sep 25', 'Sep 30'],
                counts: [45, 52, 48, 55, 60, 58, 62]
            },
            last90: {
                dates: ['Jul', 'Aug', 'Sep'],
                counts: [320, 380, 400]
            }
        }
    }
};