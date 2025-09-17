
def get_cost(injury_type):
    # Simulated costs for different injuries
    costs = {
        "shoulder": 5000,
        "back": 7000,
        "neck": 3000
    }
    return costs.get(injury_type.lower(), 0)

def main():
    total_losses = 0
    while True:
        # Input for each attendant
        add_another = input("Do you want to add another attendant? (yes/no): ").strip().lower()
        if add_another != 'yes':
            break
        
        # Input for attendant status
        attendant_status = input("Is the attendant injured? (yes/no): ").strip().lower()
        if attendant_status == 'yes':
            injury_location = input("How were they injured? (mattress lifting/pulling fitted sheets/bending and lifting): ").strip().lower()
            injury_type = ""
            
            if injury_location == "mattress lifting":
                injury_type = input("What type of injury? (shoulder/back/neck): ").strip().lower()
            elif injury_location == "pulling fitted sheets":
                injury_type = input("What type of injury? (shoulder/back/neck): ").strip().lower()
            elif injury_location == "bending and lifting":
                injury_type = input("What type of injury? (shoulder/back/neck): ").strip().lower()
            else:
                print("No cost for this injury location.")
                continue
            
            # Get cost based on injury type
            cost = get_cost(injury_type)
            total_losses += cost
            print(f"Workers compensation cost for {injury_type}: ${cost}")
        else:
            print("No cost for this attendant.")
    
    # Check if corporate will call
    if total_losses > 25000:
        print("CEO will schedule a call.")
    else:
        print("Total losses are within acceptable limits.")

    print(f"Total losses from workers' comp: ${total_losses}")

# Run the main function
if __name__ == "__main__":
    main()
