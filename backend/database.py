"""
FinGraph-AI In-Memory Financial Datastore
Maintains real-time state for users, accounts, devices, locations, transactions,
and system audit logs. Includes seed entities and interactive attack simulators.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from backend.models import (
    AccountInfo,
    TransactionRecord,
    TransactionCreate,
    SystemLog,
    ExpenseCategorySummary,
    ExpenseSummaryResponse
)


class FinancialDatabase:
    """In-memory datastore with relational entity tracking and audit logging."""

    def __init__(self):
        self.accounts: Dict[str, AccountInfo] = {}
        self.transactions: List[TransactionRecord] = []
        self.logs: List[SystemLog] = []
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.locations: Dict[str, Dict[str, Any]] = {}
        self.simulated_rings: List[str] = []
        self._seed_initial_data()

    def _add_log(self, level: str, category: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Append to live system audit logs."""
        log_entry = SystemLog(
            id=f"LOG-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            level=level,
            category=category,
            message=message,
            details=details or {}
        )
        self.logs.insert(0, log_entry)  # most recent first
        # Keep last 500 logs
        if len(self.logs) > 500:
            self.logs = self.logs[:500]

    def _seed_initial_data(self):
        """Seed realistic customers, merchants, devices, bank accounts, and transactions."""
        self.accounts.clear()
        self.transactions.clear()
        self.logs.clear()
        self.devices.clear()
        self.locations.clear()
        self.simulated_rings.clear()

        # 1. Hardware Devices
        self.devices = {
            "DEV-IPHONE-ALICE": {"id": "DEV-IPHONE-ALICE", "name": "Apple iPhone 15 Pro", "ip": "192.168.1.105", "os": "iOS 17.4"},
            "DEV-MACBOOK-BOB": {"id": "DEV-MACBOOK-BOB", "name": "Apple MacBook Pro M3", "ip": "192.168.1.108", "os": "macOS 14.3"},
            "DEV-PIXEL-CAROL": {"id": "DEV-PIXEL-CAROL", "name": "Google Pixel 8", "ip": "192.168.2.45", "os": "Android 14"},
            "DEV-SAMSUNG-DAVID": {"id": "DEV-SAMSUNG-DAVID", "name": "Samsung Galaxy S24", "ip": "192.168.3.72", "os": "Android 14"},
            "DEV-POS-TECHMART": {"id": "DEV-POS-TECHMART", "name": "TechMart Terminal #04", "ip": "10.0.4.12", "os": "Linux POS"},
            "DEV-POS-GOURMET": {"id": "DEV-POS-GOURMET", "name": "Bistro Clover Station", "ip": "10.0.5.18", "os": "Android POS"},
            "DEV-POS-APEX": {"id": "DEV-POS-APEX", "name": "Apex Box Office POS", "ip": "10.0.6.22", "os": "Windows POS"},
            "DEV-POS-CITYPOWER": {"id": "DEV-POS-CITYPOWER", "name": "Utility Gateway", "ip": "10.0.7.30", "os": "Linux Enterprise"},
            "DEV-GHOST-RIG-99": {"id": "DEV-GHOST-RIG-99", "name": "Virtual Multi-Instance Emulator", "ip": "198.51.100.42", "os": "Spoofed Linux / TOR Exit"}
        }

        # 2. Locations
        self.locations = {
            "LOC-NYC": {"id": "LOC-NYC", "city": "New York", "country": "USA", "region": "North America"},
            "LOC-BOS": {"id": "LOC-BOS", "city": "Boston", "country": "USA", "region": "North America"},
            "LOC-SFO": {"id": "LOC-SFO", "city": "San Francisco", "country": "USA", "region": "North America"},
            "LOC-PROXY": {"id": "LOC-PROXY", "city": "Frankfurt (VPN / Proxy Node)", "country": "DE", "region": "Europe"}
        }

        # 3. Bank Accounts (Customers, Merchants, Admin)
        seed_accounts = [
            AccountInfo(account_id="ACC-ALICE-101", customer_id="CUST-ALICE", owner_name="Alice Smith", role="Customer", balance=14250.00, status="Active", device_id="DEV-IPHONE-ALICE", location="LOC-NYC"),
            AccountInfo(account_id="ACC-BOB-202", customer_id="CUST-BOB", owner_name="Bob Jones", role="Customer", balance=8940.00, status="Active", device_id="DEV-MACBOOK-BOB", location="LOC-NYC"),
            AccountInfo(account_id="ACC-CAROL-303", customer_id="CUST-CAROL", owner_name="Carol Danvers", role="Customer", balance=6120.00, status="Active", device_id="DEV-PIXEL-CAROL", location="LOC-BOS"),
            AccountInfo(account_id="ACC-DAVID-404", customer_id="CUST-DAVID", owner_name="David Miller", role="Customer", balance=7850.00, status="Active", device_id="DEV-SAMSUNG-DAVID", location="LOC-SFO"),
            AccountInfo(account_id="ACC-TECHMART-500", customer_id="CUST-TECHMART", owner_name="TechMart Global", role="Merchant", balance=284500.00, status="Active", device_id="DEV-POS-TECHMART", location="LOC-NYC"),
            AccountInfo(account_id="ACC-GOURMET-501", customer_id="CUST-GOURMET", owner_name="Gourmet Bistro", role="Merchant", balance=48200.00, status="Active", device_id="DEV-POS-GOURMET", location="LOC-NYC"),
            AccountInfo(account_id="ACC-APEX-502", customer_id="CUST-APEX", owner_name="Apex Cinemas & Ent", role="Merchant", balance=63900.00, status="Active", device_id="DEV-POS-APEX", location="LOC-NYC"),
            AccountInfo(account_id="ACC-CITYPOWER-503", customer_id="CUST-CITYPOWER", owner_name="City Power & Utilities", role="Merchant", balance=112000.00, status="Active", device_id="DEV-POS-CITYPOWER", location="LOC-NYC"),
            
            # Seed Anomaly Ring 1: Smurfing Accounts
            AccountInfo(account_id="ACC-SMURF-SOURCE", customer_id="CUST-SMURF-MASTER", owner_name="Darkpool Trading Entity", role="Customer", balance=48000.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SMURF-MULE-1", customer_id="CUST-MULE-1", owner_name="James Mule A", role="Customer", balance=120.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SMURF-MULE-2", customer_id="CUST-MULE-2", owner_name="Karen Mule B", role="Customer", balance=85.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SMURF-MULE-3", customer_id="CUST-MULE-3", owner_name="Victor Mule C", role="Customer", balance=210.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SMURF-AGGREGATOR", customer_id="CUST-AGGREGATOR", owner_name="Panama Shell Corp Aggregator", role="Customer", balance=39400.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),

            # Seed Anomaly Ring 2: Shared-Device Syndicate Accounts
            AccountInfo(account_id="ACC-SYNDICATE-801", customer_id="CUST-SYN-1", owner_name="Compromised Profile #1", role="Customer", balance=340.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SYNDICATE-802", customer_id="CUST-SYN-2", owner_name="Compromised Profile #2", role="Customer", balance=450.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SYNDICATE-803", customer_id="CUST-SYN-3", owner_name="Compromised Profile #3", role="Customer", balance=620.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
            AccountInfo(account_id="ACC-SYNDICATE-804", customer_id="CUST-SYN-4", owner_name="Compromised Profile #4", role="Customer", balance=280.00, status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"),
        ]

        for acc in seed_accounts:
            self.accounts[acc.account_id] = acc

        # 4. Seed Legitimate Transactions
        seed_txs = [
            # Alice Transactions
            TransactionRecord(
                tx_id="TX-ALICE-01", timestamp="2026-10-05 12:30:15",
                sender_account="ACC-ALICE-101", sender_name="Alice Smith",
                recipient_account="ACC-GOURMET-501", recipient_name="Gourmet Bistro",
                amount=68.50, type="Payment", category="Food",
                description="Team business lunch", predicted_frequency="Weekly"
            ),
            TransactionRecord(
                tx_id="TX-ALICE-02", timestamp="2026-10-05 18:45:00",
                sender_account="ACC-ALICE-101", sender_name="Alice Smith",
                recipient_account="ACC-APEX-502", recipient_name="Apex Cinemas & Ent",
                amount=35.00, type="Purchase", category="Entertainment",
                description="Weekend IMAX tickets", predicted_frequency="Weekly"
            ),
            TransactionRecord(
                tx_id="TX-ALICE-03", timestamp="2026-10-06 09:15:20",
                sender_account="ACC-ALICE-101", sender_name="Alice Smith",
                recipient_account="ACC-CITYPOWER-503", recipient_name="City Power & Utilities",
                amount=142.80, type="Payment", category="Bills",
                description="Monthly electric and grid utility bill", predicted_frequency="Monthly"
            ),
            TransactionRecord(
                tx_id="TX-ALICE-04", timestamp="2026-10-06 14:10:44",
                sender_account="ACC-ALICE-101", sender_name="Alice Smith",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=249.99, type="Purchase", category="Shopping",
                description="Noise cancelling headphones", predicted_frequency="Rare / One-off"
            ),
            TransactionRecord(
                tx_id="TX-ALICE-05", timestamp="2026-10-07 10:00:12",
                sender_account="ACC-ALICE-101", sender_name="Alice Smith",
                recipient_account="ACC-BOB-202", recipient_name="Bob Jones",
                amount=85.00, type="Transfer", category="Sports",
                description="Gym membership and racket club split", predicted_frequency="Monthly"
            ),
            TransactionRecord(
                tx_id="TX-ALICE-06", timestamp="2026-10-07 13:20:05",
                sender_account="ACC-ALICE-101", sender_name="Alice Smith",
                recipient_account="ACC-GOURMET-501", recipient_name="Gourmet Bistro",
                amount=24.50, type="Payment", category="Food",
                description="Espresso and bakery snacks", predicted_frequency="Daily"
            ),

            # Bob Transactions
            TransactionRecord(
                tx_id="TX-BOB-01", timestamp="2026-10-04 11:20:00",
                sender_account="ACC-BOB-202", sender_name="Bob Jones",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=450.00, type="Purchase", category="Shopping",
                description="4K Monitor for home desk", predicted_frequency="Rare / One-off"
            ),
            TransactionRecord(
                tx_id="TX-BOB-02", timestamp="2026-10-06 20:10:00",
                sender_account="ACC-BOB-202", sender_name="Bob Jones",
                recipient_account="ACC-APEX-502", recipient_name="Apex Cinemas & Ent",
                amount=52.00, type="Payment", category="Entertainment",
                description="Film festival passes", predicted_frequency="Monthly"
            ),

            # Carol Transactions
            TransactionRecord(
                tx_id="TX-CAROL-01", timestamp="2026-10-06 17:30:00",
                sender_account="ACC-CAROL-303", sender_name="Carol Danvers",
                recipient_account="ACC-GOURMET-501", recipient_name="Gourmet Bistro",
                amount=84.00, type="Payment", category="Food",
                description="Family dinner", predicted_frequency="Weekly"
            ),
        ]

        # 5. Pre-staged Smurfing Transactions (Structured just under 5k threshold, funneling to aggregator)
        smurf_txs = [
            TransactionRecord(
                tx_id="TX-SMURF-01", timestamp="2026-10-07 02:11:00",
                sender_account="ACC-SMURF-SOURCE", sender_name="Darkpool Trading Entity",
                recipient_account="ACC-SMURF-MULE-1", recipient_name="James Mule A",
                amount=4950.00, type="Transfer", category="Bills",
                description="Disbursement consulting batch 1", predicted_frequency="Rare / One-off",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SMURF-02", timestamp="2026-10-07 02:14:30",
                sender_account="ACC-SMURF-SOURCE", sender_name="Darkpool Trading Entity",
                recipient_account="ACC-SMURF-MULE-2", recipient_name="Karen Mule B",
                amount=4890.00, type="Transfer", category="Bills",
                description="Disbursement consulting batch 2", predicted_frequency="Rare / One-off",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SMURF-03", timestamp="2026-10-07 02:17:15",
                sender_account="ACC-SMURF-SOURCE", sender_name="Darkpool Trading Entity",
                recipient_account="ACC-SMURF-MULE-3", recipient_name="Victor Mule C",
                amount=4920.00, type="Transfer", category="Bills",
                description="Disbursement consulting batch 3", predicted_frequency="Rare / One-off",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SMURF-04", timestamp="2026-10-07 03:02:10",
                sender_account="ACC-SMURF-MULE-1", sender_name="James Mule A",
                recipient_account="ACC-SMURF-AGGREGATOR", recipient_name="Panama Shell Corp Aggregator",
                amount=4830.00, type="Transfer", category="Shopping",
                description="Asset consolidation wire 01", predicted_frequency="Rare / One-off",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SMURF-05", timestamp="2026-10-07 03:04:40",
                sender_account="ACC-SMURF-MULE-2", sender_name="Karen Mule B",
                recipient_account="ACC-SMURF-AGGREGATOR", recipient_name="Panama Shell Corp Aggregator",
                amount=4805.00, type="Transfer", category="Shopping",
                description="Asset consolidation wire 02", predicted_frequency="Rare / One-off",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SMURF-06", timestamp="2026-10-07 03:08:12",
                sender_account="ACC-SMURF-MULE-3", sender_name="Victor Mule C",
                recipient_account="ACC-SMURF-AGGREGATOR", recipient_name="Panama Shell Corp Aggregator",
                amount=4710.00, type="Transfer", category="Shopping",
                description="Asset consolidation wire 03", predicted_frequency="Rare / One-off",
                is_flagged=True
            ),
        ]

        # 6. Pre-staged Syndicate Rapid Micropayments (Shared device rig, velocity burst)
        syndicate_txs = [
            TransactionRecord(
                tx_id="TX-SYN-01", timestamp="2026-10-07 04:15:02",
                sender_account="ACC-SYNDICATE-801", sender_name="Compromised Profile #1",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=320.00, type="Purchase", category="Shopping",
                description="Gift card code purchase batch #1", predicted_frequency="Daily",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SYN-02", timestamp="2026-10-07 04:15:35",
                sender_account="ACC-SYNDICATE-802", sender_name="Compromised Profile #2",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=320.00, type="Purchase", category="Shopping",
                description="Gift card code purchase batch #2", predicted_frequency="Daily",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SYN-03", timestamp="2026-10-07 04:16:10",
                sender_account="ACC-SYNDICATE-803", sender_name="Compromised Profile #3",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=320.00, type="Purchase", category="Shopping",
                description="Gift card code purchase batch #3", predicted_frequency="Daily",
                is_flagged=True
            ),
            TransactionRecord(
                tx_id="TX-SYN-04", timestamp="2026-10-07 04:16:45",
                sender_account="ACC-SYNDICATE-804", sender_name="Compromised Profile #4",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=320.00, type="Purchase", category="Shopping",
                description="Gift card code purchase batch #4", predicted_frequency="Daily",
                is_flagged=True
            ),
        ]

        self.transactions.extend(seed_txs)
        self.transactions.extend(smurf_txs)
        self.transactions.extend(syndicate_txs)

        # Audit logs initialization
        self._add_log("INFO", "SECURITY", "FinGraph-AI multi-dimensional graph datastore initialized.")
        self._add_log("INFO", "AUTH", "User session opened: Alice Smith (Customer).")
        self._add_log("INFO", "TRANSACTION", "Processed payment $68.50 from ACC-ALICE-101 to ACC-GOURMET-501 (Food).")
        self._add_log("WARN", "GRAPH_SCAN", "Elevated pass-through velocity detected across 3 intermediate mule nodes.")
        self._add_log("FRAUD_ALERT", "ML_INFERENCE", "XGBoost + SHAP flagged Smurfing Ring CLUSTER-SMURF-01 with 99.8% confidence.")
        self._add_log("FRAUD_ALERT", "ML_INFERENCE", "XGBoost + SHAP flagged Device Syndicate CLUSTER-SYN-RIG-99 (4 accounts on DEV-GHOST-RIG-99).")

    def record_user_transaction(self, req: TransactionCreate) -> TransactionRecord:
        """Processes transaction from User Portal, validates accounts, updates balance, and logs."""
        sender = self.accounts.get(req.sender_account)
        if not sender:
            raise ValueError(f"Sender account {req.sender_account} not found.")
        
        recipient = self.accounts.get(req.recipient_account)
        recipient_name = recipient.owner_name if recipient else "External Destination"

        if sender.balance < req.amount:
            raise ValueError(f"Insufficient balance. Current balance is ${sender.balance:,.2f}.")

        # Deduct sender balance and credit recipient if internal
        sender.balance -= req.amount
        if recipient:
            recipient.balance += req.amount

        tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        tx = TransactionRecord(
            tx_id=tx_id,
            timestamp=timestamp,
            sender_account=req.sender_account,
            sender_name=sender.owner_name,
            recipient_account=req.recipient_account,
            recipient_name=recipient_name,
            amount=round(req.amount, 2),
            type=req.type,
            category=req.category,
            description=req.description,
            predicted_frequency=req.predicted_frequency,
            status="COMPLETED",
            is_flagged=False
        )
        self.transactions.insert(0, tx)

        # Log event
        self._add_log(
            level="INFO",
            category="TRANSACTION",
            message=f"User {sender.owner_name} submitted {req.type} of ${req.amount:,.2f} to {recipient_name} [{req.category}: {req.description} | {req.predicted_frequency}].",
            details={
                "tx_id": tx_id,
                "amount": req.amount,
                "category": req.category,
                "frequency": req.predicted_frequency
            }
        )

        return tx

    def get_user_expenses(self, account_id: str) -> ExpenseSummaryResponse:
        """Computes spending breakdown by category for dynamic pie chart."""
        user_txs = [t for t in self.transactions if t.sender_account == account_id]
        inflow_txs = [t for t in self.transactions if t.recipient_account == account_id]

        total_spent = sum(t.amount for t in user_txs)
        total_inflow = sum(t.amount for t in inflow_txs)

        category_map: Dict[str, Dict[str, Any]] = {
            "Food": {"amount": 0.0, "count": 0},
            "Entertainment": {"amount": 0.0, "count": 0},
            "Sports": {"amount": 0.0, "count": 0},
            "Shopping": {"amount": 0.0, "count": 0},
            "Bills": {"amount": 0.0, "count": 0}
        }

        for t in user_txs:
            cat = t.category if t.category in category_map else "Shopping"
            category_map[cat]["amount"] += t.amount
            category_map[cat]["count"] += 1

        categories_summary: List[ExpenseCategorySummary] = []
        for cat, data in category_map.items():
            amt = round(data["amount"], 2)
            pct = round((amt / total_spent * 100), 1) if total_spent > 0 else 0.0
            categories_summary.append(ExpenseCategorySummary(
                category=cat,
                total_amount=amt,
                percentage=pct,
                tx_count=data["count"]
            ))

        return ExpenseSummaryResponse(
            account_id=account_id,
            total_spent=round(total_spent, 2),
            total_inflow=round(total_inflow, 2),
            categories=categories_summary,
            recent_transactions=user_txs[:15]
        )

    def trigger_dynamic_smurfing_simulation(self) -> str:
        """Dynamically injects a new high-confidence Smurfing Ring into the live graph."""
        ring_num = len(self.simulated_rings) + 1
        ring_id = f"CLUSTER-LIVE-SMURF-{ring_num:02d}"
        self.simulated_rings.append(ring_id)

        source_id = f"ACC-LIVE-SRC-{ring_num}"
        agg_id = f"ACC-LIVE-AGG-{ring_num}"
        
        self.accounts[source_id] = AccountInfo(
            account_id=source_id, customer_id=f"CUST-SRC-{ring_num}",
            owner_name=f"Shadow FinCorp #{ring_num}", role="Customer", balance=60000.0,
            status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"
        )
        self.accounts[agg_id] = AccountInfo(
            account_id=agg_id, customer_id=f"CUST-AGG-{ring_num}",
            owner_name=f"Offshore Vault #{ring_num}", role="Customer", balance=500.0,
            status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"
        )

        # Create 4 mules
        mule_ids = []
        for i in range(1, 5):
            m_id = f"ACC-LIVE-MULE-{ring_num}-{i}"
            mule_ids.append(m_id)
            self.accounts[m_id] = AccountInfo(
                account_id=m_id, customer_id=f"CUST-MULE-{ring_num}-{i}",
                owner_name=f"Live Mule #{ring_num}-{i}", role="Customer", balance=50.0,
                status="Monitored", device_id="DEV-GHOST-RIG-99", location="LOC-PROXY"
            )

            # Fan-out tx: Source -> Mule ($4,850)
            self.transactions.insert(0, TransactionRecord(
                tx_id=f"TX-LIVE-SMURF-IN-{ring_num}-{i}",
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                sender_account=source_id, sender_name=f"Shadow FinCorp #{ring_num}",
                recipient_account=m_id, recipient_name=f"Live Mule #{ring_num}-{i}",
                amount=4850.0 + (i * 25), type="Transfer", category="Bills",
                description="Restructured settlement", predicted_frequency="Rare / One-off",
                is_flagged=True
            ))

            # Fan-in tx: Mule -> Aggregator ($4,790)
            self.transactions.insert(0, TransactionRecord(
                tx_id=f"TX-LIVE-SMURF-OUT-{ring_num}-{i}",
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                sender_account=m_id, sender_name=f"Live Mule #{ring_num}-{i}",
                recipient_account=agg_id, recipient_name=f"Offshore Vault #{ring_num}",
                amount=4790.0 + (i * 20), type="Transfer", category="Shopping",
                description="Vault deposit split", predicted_frequency="Rare / One-off",
                is_flagged=True
            ))

        self._add_log(
            "FRAUD_ALERT", "GRAPH_SCAN",
            f"⚡ ATTACK SIMULATION INJECTED: New Smurfing Ring {ring_id} detected across {len(mule_ids)+2} nodes.",
            {"ring_id": ring_id, "nodes": [source_id, agg_id] + mule_ids}
        )
        return ring_id

    def trigger_dynamic_syndicate_simulation(self) -> str:
        """Dynamically injects a new high-confidence Fraud Syndicate into the live graph."""
        ring_num = len(self.simulated_rings) + 1
        ring_id = f"CLUSTER-LIVE-SYNDICATE-{ring_num:02d}"
        self.simulated_rings.append(ring_id)

        device_id = f"DEV-BOTNET-RIG-{ring_num:02d}"
        self.devices[device_id] = {
            "id": device_id,
            "name": f"Automated Botnet Rig #{ring_num}",
            "ip": f"203.0.113.{50 + ring_num}",
            "os": "Headless Chromium Cluster"
        }

        # Create 5 synthetic identity accounts sharing this single botnet device
        synd_accs = []
        for i in range(1, 6):
            acc_id = f"ACC-BOT-SYN-{ring_num}-{i}"
            synd_accs.append(acc_id)
            self.accounts[acc_id] = AccountInfo(
                account_id=acc_id, customer_id=f"CUST-BOT-{ring_num}-{i}",
                owner_name=f"Synthetic Bot Account #{i}", role="Customer", balance=150.0,
                status="Monitored", device_id=device_id, location="LOC-PROXY"
            )

            # Rapid burst payment to Merchant
            self.transactions.insert(0, TransactionRecord(
                tx_id=f"TX-BOT-BURST-{ring_num}-{i}",
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                sender_account=acc_id, sender_name=f"Synthetic Bot Account #{i}",
                recipient_account="ACC-TECHMART-500", recipient_name="TechMart Global",
                amount=499.00, type="Purchase", category="Shopping",
                description="Automated digital card redemption", predicted_frequency="Daily",
                is_flagged=True
            ))

        self._add_log(
            "FRAUD_ALERT", "SECURITY",
            f"🚨 ATTACK SIMULATION INJECTED: Coordinated Fraud Syndicate {ring_id} detected! 5 distinct accounts sharing {device_id}.",
            {"ring_id": ring_id, "device_id": device_id, "accounts": synd_accs}
        )
        return ring_id

    def reset(self):
        """Resets the in-memory database back to baseline seed state."""
        self._seed_initial_data()
        self._add_log("INFO", "SECURITY", "Datastore reset to clean baseline configuration.")


# Global singleton database instance
db = FinancialDatabase()
