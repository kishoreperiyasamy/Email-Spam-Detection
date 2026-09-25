import os
import csv
import random

def generate_dataset():
    dataset_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(dataset_dir, 'spam_emails.csv')

    # Seeded for reproducible quality
    random.seed(42)

    spam_samples = [
        # Phishing / Account Verification
        ("URGENT: Your PayPal Account Has Been Suspended", 
         "Dear customer, We detected unauthorized login attempts from an unknown IP address. Your account is temporarily locked. Please verify your credentials and update your credit card immediately at http://192.168.1.55/paypal-verify to restore full access. Failure to do so within 24 hours will result in permanent account termination."),
        
        ("Action Required: Unusual Sign-in Activity Detected on your Bank Account", 
         "Security Alert: Your online banking session was flagged for suspicious activity. To protect your funds, click the link below to confirm your identity and social security number. Failure to verify will freeze your checking account. Verify here: http://secure-chase-update.info/login"),
        
        ("Netflix Billing Issue: Update your payment method immediately", 
         "We were unable to process your monthly subscription payment. Your membership is on hold. Please update your billing details and credit card information right now at http://netflix-member-update.top/account to prevent cancellation."),
        
        ("Microsoft Account Security: Password expires in 2 hours", 
         "Your Office 365 password expires today. Keep your current password by verifying your credentials through our IT helpdesk portal: http://portal-office365-verify.com/login. Failure to verify will prevent you from accessing work emails."),

        ("Amazon Notification: Your order has been placed ($1,499.00)", 
         "Thank you for your order #892-119283 for Apple iPhone 15 Pro Max. If you did not make this purchase, call our fraud prevention hotline immediately at 1-800-FAKE-NUM or cancel the transaction here: http://amazon-cancel-order.net/dispute"),

        ("Apple ID Locked: Unauthorized purchase of App Store Gift Card", 
         "Your Apple ID was used to purchase a $500 App Store Gift Card from an unrecognized device. If this was not you, verify your security questions and card information at http://appleid-verify-alert.com to unlock your account."),

        ("IRS Tax Refund Notification: You have an unclaimed refund of $4,280", 
         "Internal Revenue Service Official Notice: Our records indicate you are eligible for an unclaimed tax return payment. Submit your direct deposit bank details, SSN, and full name at http://irs-refund-claim-portal.gov.fake.org/refund to receive immediate payout."),

        ("Google Alert: Critical Security Vulnerability on your Gmail", 
         "Someone knows your password! We blocked a suspicious sign-in from Moscow, Russia. Please review your account activity and enter your recovery code at http://google-security-notice.xyz/checkpoint to ensure your messages remain safe."),

        ("Dropbox: Action required on shared sensitive document", 
         "Human Resources shared a confidential document 'Q3_Payroll_Adjustment.pdf' with you on Dropbox. Click here to log in with your email password to decrypt and view the document: http://dropbox-secure-share.org/auth"),

        ("FedEx: Delivery Failed - Package Pending at Warehouse", 
         "We attempted to deliver parcel #FDX-994827 today but no recipient was available. A delivery rescheduling fee of $2.99 is required. Update your address and pay with debit card: http://fedex-parcel-redelivery.site/track"),

        # Lottery / Prizes / Giveaways
        ("CONGRATULATIONS! You have won $2,500,000 in the International Mega Lottery", 
         "Official Notification: Your email address was selected in the category 'A' draws of the Euro Million Lottery. You have won a cash lump sum of $2,500,000.00 USD! Send your full name, passport copy, telephone number, and bank details to agent Dr. Mark Benson at claim-dept@lottery-winner.biz to receive funds."),

        ("You have been chosen for a $1,000 Walmart Gift Card!", 
         "Special Promotion: You are the lucky visitor of the day! Claim your free $1,000 Walmart Gift Card right now. Only 3 cards left in your area. Click here to claim your reward instantly: http://free-gift-cards-now.online/walmart"),

        ("EXCLUSIVE PRIZE: Claim your free luxury cruise vacation!", 
         "Pack your bags! You have won an all-inclusive 7-day Caribbean cruise for two people. Call 1-888-WIN-TRIP now or visit http://luxury-cruise-giveaway.club. Must claim within 48 hours. No purchase necessary!"),

        ("Urgent Notification: Final Notice to Claim Your Sweepstakes Prize", 
         "This is your final warning. Your check of $750,000 is waiting at our processing center. If you do not claim it today, it will be forfeited to the runner up. Enter your address and wire transfer details at http://sweepstakes-winners-portal.com"),

        ("You Won! Free iPhone 16 Pro Max Giveaway Winner Selected", 
         "Dear lucky winner! You have been selected in our monthly electronic giveaway raffle. To confirm shipping of your brand new iPhone 16 Pro Max, pay $1.00 for customs processing here: http://win-new-iphone-pro.biz/claim"),

        # Financial / Investment Scams / Crypto
        ("GUARANTEED 500% RETURN: Next 100x Crypto Gem Revealed", 
         "Don't miss the biggest crypto boom in history! Our secret AI automated trading bot guarantees 500% weekly returns. Deposit 0.05 BTC or $250 USDT today and watch your wallet grow automatically. Sign up: http://crypto-wealth-bot.io/invest"),

        ("Confidential Business Proposal: Urgent Assistance Needed ($35 Million USD)", 
         "Dear Friend, I am Mr. David Cole, audit manager at a reputable bank in London. There exists a dormant balance of $35,500,000.00 from a deceased foreign national. I propose to transfer these funds into your account as the next of kin. You will receive 40% share. Reply with your telephone number and bank routing code."),

        ("Pre-Approved Fast Loan: Up to $50,000 with 0% Interest for 12 Months", 
         "Bad credit? No credit? No problem! Get instant cash deposited into your bank account in 15 minutes. No paperwork, no credit check required. Apply online now: http://instant-cash-express-loans.net/apply"),

        ("Work from Home Opportunity: Earn $3,000 to $5,000 Weekly Posting Reviews", 
         "Start making money from home with just a smartphone! Global brands need users to write short reviews. No experience needed. Guaranteed daily payouts directly to your PayPal or Venmo. Register here: http://easy-home-profits.click/start"),

        ("Investment Alert: Double your Bitcoin in 24 Hours!", 
         "Send any amount of BTC to our verified smart contract wallet and our high-frequency arbitrage algorithms will send back 200% within 24 hours. Over $10M paid out! Join the pool now: http://btc-doubler-matrix.org"),

        # Promotional & Excessive Marketing
        ("FLASH SALE: 90% OFF Ray-Ban Sunglasses and Luxury Watches Today Only!", 
         "HUGE CLEARANCE SALE! Brand new polarized designer sunglasses and luxury wristwatches starting at just $19.99! Limited stock available. Buy 2 get 1 FREE! Click here to shop the secret VIP discount: http://luxury-outlet-deals.shop"),

        ("Overnight Weight Loss Miracle Pill: Melt 20 lbs in 14 Days without Dieting", 
         "Doctors hate this secret! Clinical trials prove our herbal keto formula burns belly fat while you sleep. 100% natural, FDA approved ingredients. Order today and get 3 bottles free plus complimentary shipping: http://miracle-keto-burn.top"),

        ("Boost Your Website Ranking to #1 on Google - Guaranteed SEO Services", 
         "Dear webmaster, We can get your website on the first page of Google search within 30 days! Increase your sales, web traffic, and revenue 10x. Special discounted package of 5,000 backlinks for only $49. Buy now: http://cheap-seo-backlinks.biz"),

        ("Cheapest Pharmacy Online: Viagra, Cialis, Xanax without Prescription", 
         "Best online drugstore with discreet worldwide shipping! Save up to 85% on all generic medications. No doctor visit required, completely anonymous packaging. Order your pills online today: http://global-meds-discount.org"),

        ("Urgent: Your Auto Warranty is About to Expire!", 
         "Final notice regarding your vehicle service contract. Your extended warranty coverage has lapsed. Avoid thousands in costly repair bills by renewing today. Call our warranty specialists at 1-800-555-CAR or visit http://vehicle-warranty-renewal.com")
    ]

    ham_samples = [
        # Work & Collaboration
        ("Project Status Update: Q3 Sprint Review Agenda and Deliverables", 
         "Hi Team, Here is the agenda for tomorrow's Q3 sprint review at 10:00 AM in Conference Room B. We will review completed frontend components, database migration milestones, and test coverage. Please update your Jira tickets before the meeting. The slides are attached to the team drive. Best regards, Sarah."),
        
        ("Meeting Notes: Architecture Review and API Design Discussion", 
         "Hello everyone, Thank you for attending today's architecture discussion. Key takeaways: 1. We will use PostgreSQL connection pooling to handle concurrent requests. 2. Frontend will interact through REST endpoints. 3. Code review deadline is Friday 5 PM. Let me know if anyone has questions."),

        ("Pull Request #142 Ready for Review: Added User Profile and Auth Guard", 
         "Hey Alex, I have pushed the changes for user session management and profile updates. The unit tests pass locally with 98% coverage. Could you please take a look and approve the PR when you have time? Link: git-repo.internal/pr/142. Thanks!"),

        ("Quarterly Budget Planning and Resource Allocation Meeting", 
         "Dear Department Leads, Please submit your software licensing requests and hardware expenditure estimates for the upcoming fiscal quarter by Wednesday afternoon. We will compile everything into the master budget spreadsheet. Thank you for your cooperation."),

        ("Interview Schedule: Senior Software Engineer Candidate - John Smith", 
         "Hi Mark and Priya, You are scheduled to interview John Smith for the Senior Backend Engineer position on Thursday from 2:00 PM to 3:30 PM. The candidate's resume and coding challenge submission are attached. Please submit your scorecard immediately following the call."),

        ("Office Closure Notice: Public Holiday next Monday", 
         "Dear Colleagues, Please be reminded that the company offices will be closed next Monday in observance of the public holiday. Regular operations and customer support will resume on Tuesday morning. Have a safe and restful long weekend!"),

        ("New Employee Welcome: Welcome Alex to the Engineering Team!", 
         "Please join us in welcoming Alex Rivera, who joins our team today as a DevOps Engineer. Alex brings over 6 years of experience in cloud infrastructure, Kubernetes, and CI/CD automation. Stop by desk 14 to say hello!"),

        ("Weekly Engineering Team Lunch and Knowledge Sharing Session", 
         "Hey folks! It's Friday lunch time. We are ordering Thai food today for the knowledge sharing session. David will give a 20-minute lightning talk on TF-IDF vectorization and text classification algorithms. Meet in the 4th floor lounge at 12:30 PM."),

        ("Code Freeze Notice: Version 2.4 Production Release", 
         "Attention all developers: The code freeze for v2.4 begins tonight at 8:00 PM EST. Only critical bug fixes with manager sign-off will be merged after this window. QA regression testing begins tomorrow at 9 AM."),

        ("Client Proposal Draft: Feedback requested on technical specifications", 
         "Hi Rachel, I drafted the proposal document for the Acme Corp cloud migration project. Could you review Section 4 regarding database failover strategies and SLA guarantees before we present it to the client tomorrow? Thank you, James."),

        # Personal Communication
        ("Dinner plans this Saturday at Italian Bistro", 
         "Hey! Hope you are having a wonderful week. Are you still free for dinner this Saturday around 7:30 PM? We found a great Italian restaurant downtown with fantastic pasta. Let me know if that time works for you so I can make a reservation."),

        ("Weekend Hiking Trip to Blue Ridge Trail", 
         "Hi friends, The weather looks sunny and clear this Sunday. We are planning a 5-mile hike at Blue Ridge Trail, starting at 9:00 AM from the north entrance parking lot. Bring water, trail snacks, and comfortable shoes. Reply if you can make it!"),

        ("Photos from last weekend's family gathering", 
         "Hi Mom, I just finished sorting through the photos we took during Grandma's 80th birthday party last weekend. Everyone looked so happy! I put them in our shared Google Drive folder so everyone can download high-resolution copies."),

        ("Book Club Discussion: Chapter 4 to 7 Notes", 
         "Hi all, For our next book club meetup on Tuesday, please finish reading through Chapter 7. Think about the author's character development and thematic pacing. Looking forward to hearing everyone's thoughts over tea!"),

        ("Gym Workout Schedule and Fitness Goals for Next Month", 
         "Hey brother, Let's get back to our regular gym schedule. Thinking Monday, Wednesday, and Friday at 6:30 AM before work. Let me know if you want to focus on strength training or cardio this month."),

        # Transactional & Utility
        ("Your Amazon.com Order #112-984716 has been delivered", 
         "Your package containing 'Data Science from Scratch by Joel Grus' was handed directly to a resident at your front door. If you did not receive this delivery, check your mailbox or contact customer service."),

        ("Flight Confirmation: Roundtrip to Chicago (Booking Ref: K8Y2LA)", 
         "United Airlines Confirmation: Your flight UA-428 departs San Francisco (SFO) at 08:15 AM on October 14, arriving in Chicago (ORD) at 14:20 PM. Seat assignment: 12B. Online check-in opens 24 hours prior to departure."),

        ("Appointment Reminder: Dental Cleaning with Dr. Evans tomorrow at 3:00 PM", 
         "This is an automated reminder of your upcoming dental checkup on Thursday, September 18 at 3:00 PM at Downtown Dental Care. Please arrive 10 minutes early to complete health updates. Reply C to confirm or call 555-0199 to reschedule."),

        ("Your Monthly Electricity Statement is Ready to View", 
         "Your Pacific Power statement for August is now available. Total amount due: $78.42, payable by October 5. Automatic payment is scheduled for your primary checking account on October 3. Thank you for your continued service."),

        ("GitHub: [spam-shield/core] Issue #42 closed by maintainer", 
         "Issue #42 'Improve TF-IDF tokenization speed for large text batches' has been closed with commit 7fa98b. You are receiving this email because you subscribed to notifications on this repository.")
    ]

    # Expand dataset with variations, paraphrasing, and diverse samples
    rows = []
    
    # Generate variations of spam
    spam_templates = [
        ("URGENT: {service} Account Alert", 
         "Dear customer, We noticed suspicious login activity on your {service} account from {location}. Verify your identity immediately: http://verify-{service_slug}-auth.com/{token} or your account will be permanently blocked within {hours} hours."),
        
        ("Payment Declined: {service} Subscription Suspended", 
         "We were unable to charge your card on file for {service}. To avoid interruption of your service and loss of saved files, click here to update your payment details: http://billing-{service_slug}.info/update?id={token}"),
        
        ("CONGRATULATIONS: You have won {amount} in {lottery}!", 
         "You have been selected as the grand winner of {amount} in the {lottery}! To claim your prize, send your full name, home address, and bank wire routing number to claim-dept@{slug}-winner.org within 48 hours."),
        
        ("EXCLUSIVE OFFER: {discount}% discount on {product}", 
         "Don't miss this limited-time flash sale! Get up to {discount}% off genuine {product} with free international shipping. Click here to claim your coupon code before midnight: http://discount-{product_slug}-sale.net"),
        
        ("Instant Approval: Claim your {loan_amount} pre-approved cash loan", 
         "Congratulations! You are pre-approved for up to {loan_amount} personal loan with 0% interest for the first 6 months. No credit checks needed. Money wired in 10 minutes: http://fast-cash-{slug}.biz/apply"),
         
        ("Security Warning: Your {service} password has been breached", 
         "A data breach detected your credentials exposed. Reset your password immediately through our secure portal: http://security-{service_slug}-reset.com/auth. Failure to update may compromise your personal data."),

        ("Claim your free {gift_amount} {store} voucher today!", 
         "You are customer number 1,000 to visit our promotion page today! You qualify for a free {gift_amount} {store} gift certificate. Claim now before vouchers run out: http://promo-{store_slug}-rewards.click"),

        ("Crypto Signal: Buy {coin} before 1000% breakout!", 
         "Our insider trading group just flagged {coin} for an imminent pump! Join the VIP Telegram group and copy our whale trades: http://crypto-signals-{slug}.top/vip"),

        ("Unpaid Invoice #{invoice_num} Past Due Notification", 
         "Please find attached overdue invoice #{invoice_num} in the amount of $2,450.00. Payment is 14 days past due. Open the attached file or download remittance instructions from: http://invoice-remittance-{slug}.info/doc"),

        ("Earn ${rate}/hr working remotely from home - No experience", 
         "Global digital company is hiring remote assistants! Earn ${rate} per hour evaluating product listings and typing captions. Payouts made daily to PayPal or CashApp. Apply immediately: http://remote-jobs-{slug}.site/join")
    ]

    services = ["PayPal", "Netflix", "Chase Bank", "Bank of America", "Wells Fargo", "Microsoft", "Apple", "Google", "Amazon", "Dropbox", "Instagram", "Meta", "LinkedIn", "Venmo"]
    locations = ["Moscow, Russia", "Beijing, China", "Lagos, Nigeria", "São Paulo, Brazil", "Bucharest, Romania", "Jakarta, Indonesia"]
    lotteries = ["Euro Millions Lottery", "Global Sweepstakes Award", "UK National Lottery", "Australian Cash Draw", "FIFA World Cup Raffle"]
    products = ["Luxury Swiss Watches", "Designer Sunglasses", "Keto Weight Loss Pills", "Herbal Supplements", "SEO Optimization Packages", "Wireless Noise-Canceling Earbuds"]
    stores = ["Walmart", "Target", "Amazon", "Best Buy", "Starbucks", "Home Depot"]
    coins = ["Bitcoin", "Ethereum", "Solana", "Dogecoin", "PepeCoin"]

    # Build spam dataset
    for subj, body in spam_samples:
        rows.append({"subject": subj, "body": body, "label": "spam"})

    for i in range(275):
        tmpl = random.choice(spam_templates)
        serv = random.choice(services)
        loc = random.choice(locations)
        lot = random.choice(lotteries)
        prod = random.choice(products)
        store = random.choice(stores)
        coin = random.choice(coins)
        
        subj = tmpl[0].format(
            service=serv, service_slug=serv.lower().replace(" ", ""),
            lottery=lot, slug=random.randint(100, 999),
            discount=random.choice([70, 75, 80, 85, 90]),
            product=prod, product_slug=prod.lower().split()[0],
            loan_amount=f"${random.randint(5, 50) * 1000}",
            gift_amount=f"${random.choice([250, 500, 1000])}",
            store=store, store_slug=store.lower().replace(" ", ""),
            coin=coin, invoice_num=random.randint(10000, 99999),
            rate=random.randint(35, 85),
            amount=f"${random.randint(1, 10)},000,000",
            hours=random.choice([12, 24, 48]),
            token=f"tok_{random.randint(100000, 999999)}"
        )
        body = tmpl[1].format(
            service=serv, service_slug=serv.lower().replace(" ", ""),
            location=loc, lottery=lot, slug=random.randint(100, 999),
            discount=random.choice([70, 75, 80, 85, 90]),
            product=prod, product_slug=prod.lower().split()[0],
            loan_amount=f"${random.randint(5, 50) * 1000}",
            gift_amount=f"${random.choice([250, 500, 1000])}",
            store=store, store_slug=store.lower().replace(" ", ""),
            coin=coin, invoice_num=random.randint(10000, 99999),
            rate=random.randint(35, 85),
            amount=f"${random.randint(1, 10)},000,000",
            hours=random.choice([12, 24, 48]),
            token=f"tok_{random.randint(100000, 999999)}"
        )
        rows.append({"subject": subj, "body": body, "label": "spam"})

    # Build ham dataset
    for subj, body in ham_samples:
        rows.append({"subject": subj, "body": body, "label": "ham"})

    ham_templates = [
        ("Team Sync: {topic} updates and milestones", 
         "Hi everyone, During today's meeting we will review {topic} progress for sprint {sprint}. Please ensure your branch has been merged into staging and unit tests are passing. We will meet in room {room} at {time}."),
        
        ("Notes from client consultation on {project}", 
         "Hi team, Attached are the action items from our call with {client} regarding the {project}. They loved the new user dashboard and requested minor tweaks to the reporting export. Let's aim to have these completed by {day}."),
        
        ("Code Review: Pull Request for {feature} component", 
         "Hello {colleague}, I reviewed your pull request regarding {feature}. The implementation looks clean and modular. I left two minor suggestions on line 45 regarding error boundary handling. Otherwise ready to merge!"),
         
        ("Department announcement: {event} schedule", 
         "Dear team members, The annual {event} will take place on {day} next week. The company will provide breakfast and lunch. Please RSVP by Wednesday so catering numbers can be finalized. Thanks, HR."),

        ("Lunch plans: Checking out the new {food} spot today?", 
         "Hey team! A few of us are heading over to the new {food} restaurant across the street for lunch around {time}. Would love for you to join us if you're not in meetings!"),

        ("Update regarding your subscription to {service_name}", 
         "Hello, This is a courtesy reminder that your subscription to {service_name} will automatically renew on the 15th of this month. Your payment method ending in {digits} will be charged the standard monthly fee of $9.99. No action required."),

        ("Receipt for order #{ord_num} from {store_name}", 
         "Thank you for your recent purchase at {store_name}! Your order #{ord_num} has been confirmed and is being packed. Standard delivery estimated within 3-5 business days. You can track your package inside your account portal."),

        ("Upcoming doctor appointment on {day} at {time}", 
         "Hello, this is a reminder of your medical checkup appointment on {day} at {time} with Dr. {doctor}. Please remember to bring your insurance card and a photo ID. If you need to reschedule, please call our clinic.")
    ]

    topics = ["Database Migration", "UI Design System", "Security Hardening", "Payment Gateway Integration", "Performance Benchmarking", "Search Optimization"]
    clients = ["Acme Health", "Apex Logistics", "Vanguard Financial", "Beacon Media", "Summit Retail"]
    projects = ["Mobile App V2", "Cloud Infrastructure Overhaul", "Customer Portal", "Inventory Automation"]
    colleagues = ["Sarah", "David", "Priya", "Carlos", "Emma", "Michael", "Elena"]
    events = ["Hackathon", "Quarterly All-Hands Meeting", "Diversity & Inclusion Workshop", "Engineering Offsite"]
    foods = ["Mexican Burrito", "Japanese Ramen", "Mediterranean Mezze", "Artisan Salad", "Wood-fired Pizza"]
    service_names = ["Spotify Premium", "GitHub Pro", "Medium Membership", "The New York Times", "Gym Membership"]
    store_names = ["Barnes & Noble", "Office Depot", "Patagonia", "Home Depot", "Trader Joe's Delivery"]
    doctors = ["Miller", "Watson", "Chen", "Gupta", "Adams", "Kowalski"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for i in range(280):
        tmpl = random.choice(ham_templates)
        subj = tmpl[0].format(
            topic=random.choice(topics),
            project=random.choice(projects),
            feature=random.choice(topics),
            event=random.choice(events),
            food=random.choice(foods),
            service_name=random.choice(service_names),
            ord_num=random.randint(10000, 99999),
            store_name=random.choice(store_names),
            day=random.choice(days),
            time=f"{random.choice([9, 10, 11, 1, 2, 3, 4, 5])}:{random.choice(['00', '15', '30', '45'])} {'AM' if random.random() > 0.5 else 'PM'}",
            doctor=random.choice(doctors)
        )
        body = tmpl[1].format(
            topic=random.choice(topics),
            sprint=random.randint(12, 38),
            room=f"{random.randint(1, 4)}0{random.randint(1, 9)}",
            time=f"{random.choice([9, 10, 11, 1, 2, 3, 4, 5])}:{random.choice(['00', '15', '30', '45'])} {'AM' if random.random() > 0.5 else 'PM'}",
            client=random.choice(clients),
            project=random.choice(projects),
            day=random.choice(days),
            colleague=random.choice(colleagues),
            feature=random.choice(topics),
            event=random.choice(events),
            food=random.choice(foods),
            service_name=random.choice(service_names),
            digits=f"{random.randint(1000, 9999)}",
            ord_num=random.randint(10000, 99999),
            store_name=random.choice(store_names),
            doctor=random.choice(doctors)
        )
        rows.append({"subject": subj, "body": body, "label": "ham"})

    # Shuffle rows
    random.shuffle(rows)

    with open(dataset_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "body", "label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[Dataset] Generated {len(rows)} samples ({sum(1 for r in rows if r['label'] == 'spam')} spam, {sum(1 for r in rows if r['label'] == 'ham')} ham) at {dataset_path}")

if __name__ == '__main__':
    generate_dataset()
