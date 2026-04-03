import json
import time
import random
import os
from generate_images import generate_image_from_text, check_comfyui_status

# 250 MMO RPG scenarios organized by typical MMO zones and activities
MMO_RPG_SCENARIOS = [
    # ===== STARTER ZONES (30 scenarios) =====
    "bustling starter town square with NPCs and quest givers, MMO town hub atmosphere",
    "newbie training grounds with practice dummies and wooden weapons",
    "starter inn with cozy fireplace and adventurers chatting at tables",
    "beginner blacksmith shop with simple weapons and armor displays",
    "town marketplace with colorful merchant stalls and trading NPCs",
    "starter village fountain surrounded by quest bulletin boards",
    "newbie adventurer guild hall with registration desks and job boards",
    "training academy courtyard with combat instructors and students",
    "starter town gates with guards and departing adventure parties",
    "village bakery with NPCs buying bread and basic food supplies",
    "simple potion shop with healing items and mana potions on shelves",
    "starter equipment vendor with basic gear and weapon racks",
    "town stable with horses and mount rental NPCs",
    "beginner magic shop with spell scrolls and basic enchantments",
    "starter town bank with coin storage and NPC tellers",
    "village well area with gathering NPCs and social interactions",
    "newbie crafting workshop with anvils and crafting stations",
    "starter town chapel with healing NPCs and blessing services",
    "training field with archery targets and ranged combat practice",
    "village tavern interior with bard NPCs and entertainment",
    "starter zone crossroads with signposts to different areas",
    "newbie dungeon entrance with party formation area",
    "town library with lore NPCs and skill trainers",
    "starter farm area with crop fields and NPC farmers",
    "village windmill with grain processing and fetch quests",
    "beginner fishing pond with angling NPCs and tutorial area",
    "starter camp outside town walls with tents and campfires",
    "newbie zone bridge connecting different starter areas",
    "town watchtower with scout NPCs and area surveillance",
    "starter zone monster spawning area with weak enemies",
    
    # ===== LOW-LEVEL ZONES (35 scenarios) =====
    "grassy plains with scattered monster camps and resource nodes",
    "peaceful meadow with herb gathering spots and friendly wildlife",
    "rolling hills dotted with ancient ruins and treasure chests",
    "riverside path with fishing spots and water elemental spawns",
    "flower fields with butterfly swarms and nature magic auras",
    "abandoned farmstead overrun with goblin encampments",
    "stone circle with magical energy and mini-boss encounters",
    "wooden bridge over stream with troll underneath waiting",
    "hillside cave entrance leading to underground dungeon systems",
    "old watchtower ruins with undead spawns and loot containers",
    "crystal formation area with mining nodes and earth elementals",
    "enchanted grove with fairy NPCs and nature quests",
    "bandit camp in forest clearing with multiple enemy tents",
    "ancient statue monument with puzzle mechanics and hidden rewards",
    "shallow lake with aquatic monsters and underwater treasure",
    "windswept plateau with flying creatures and aerial combat",
    "mushroom forest with toxic spores and alchemical ingredients",
    "rocky outcropping with cliff climbing and parkour elements",
    "shepherd's hut with NPC questgiver and livestock protection missions",
    "crossroads shrine with fast travel options and blessing buffs",
    "mining outpost with dwarf NPCs and ore processing facilities",
    "lumber camp with tree-cutting activities and bear encounters",
    "merchant caravan rest stop with trading and escort missions",
    "wildflower valley with seasonal events and festival decorations",
    "stone bridge ruins with gap-jumping puzzles and hidden passages",
    "berry picking grove with gathering quests and animal friends",
    "old cemetery with ghost spawns and supernatural mysteries",
    "hunter's lodge with tracking quests and trophy displays",
    "scenic overlook with panoramic views and screenshot opportunities",
    "babbling brook with stepping stones and water-walking challenges",
    "field of wheat with harvest festivals and farming activities",
    "ancient tree with druid NPCs and nature transformation magic",
    "hilltop camp with telescope NPC and stargazing activities",
    "flower garden maze with puzzle-solving and hidden NPCs",
    "peaceful glade with meditation spots and spiritual quests",
    
    # ===== MID-LEVEL DUNGEONS (30 scenarios) =====
    "dark stone dungeon corridor with glowing crystal lighting",
    "underground chamber with pools of water and echo effects",
    "dungeon treasury room filled with gold coins and rare items",
    "prison cell block with skeleton remains and rusty chains",
    "ritual chamber with arcane symbols and summoning circles",
    "flooded dungeon level with partially submerged walkways",
    "library dungeon with ancient tomes and knowledge-seeking undead",
    "forge room with lava channels and fire elemental encounters",
    "crystal cavern with prismatic light effects and gem mining",
    "bone-filled crypt with necromancer activities and undead hordes",
    "underground lake with boat crossing and aquatic monsters",
    "maze-like passages with trap mechanisms and puzzle doors",
    "dungeon boss chamber with elevated platform and dramatic lighting",
    "alchemy laboratory with bubbling cauldrons and potion ingredients",
    "underground greenhouse with corrupted plants and nature magic",
    "mining shaft with minecart tracks and cave-in hazards",
    "temple ruins with crumbling pillars and divine magic residue",
    "spider nest cavern with web-covered walls and arachnid spawns",
    "ice cave with frozen waterfalls and slippery combat surfaces",
    "volcanic dungeon with lava flows and fire-resistant enemies",
    "abandoned dwarven halls with mechanical traps and steam vents",
    "underwater ruins with air pocket rooms and aquatic challenges",
    "mushroom cavern with bioluminescent fungi and poison effects",
    "crystal mine with unstable magic and elemental storm effects",
    "underground arena with gladiator fights and spectator areas",
    "tomb complex with mummy wrappings and ancient curse effects",
    "sewer system with flowing water and disease-carrying enemies",
    "cave painting gallery with ancient history and lore discoveries",
    "underground waterfall chamber with mist effects and echo sounds",
    "dungeon elevator shaft with multiple floor access and ambushes",
    
    # ===== HIGH-LEVEL ZONES (35 scenarios) =====
    "volcanic wasteland with lava geysers and fire-immune creatures",
    "frozen tundra with howling winds and ice elemental territories",
    "corrupted forest with twisted trees and dark magic corruption",
    "floating sky island with cloud bridges and aerial platforms",
    "desert oasis with mirages and sand elemental encounters",
    "magical academy campus with spell practice areas and arcane research",
    "ancient battlefield with ghostly apparitions and war memories",
    "crystal spire tower with floating platforms and energy conduits",
    "shadow realm gateway with dimensional rifts and void creatures",
    "elemental nexus with swirling energies and primal magic",
    "cursed swampland with will-o'-wisps and bog creatures",
    "mountain peak temple with wind effects and sky-touching architecture",
    "time-distorted zone with temporal anomalies and chronological puzzles",
    "ethereal plane with translucent structures and spirit encounters",
    "demon-infested canyon with sulfur pits and infernal creatures",
    "celestial observatory with star maps and cosmic magic",
    "underwater city ruins with bubble shields and aquatic civilization",
    "gravity-defying zone with upside-down terrain and physics puzzles",
    "petrified forest with stone trees and earth elemental guardians",
    "nightmare realm with surreal landscapes and fear-based enemies",
    "arcane library dimension with infinite bookshelves and knowledge spirits",
    "plague-touched village with quarantine barriers and disease effects",
    "storm-wracked coastline with lightning strikes and tempest elementals",
    "crystal palace with prismatic walls and light-based magic",
    "void-touched wasteland with reality tears and cosmic horrors",
    "elemental forge with creation magic and primordial energies",
    "astral projection area with soul travel and spirit quests",
    "chaos realm with randomly shifting terrain and unpredictable magic",
    "divine sanctum with holy light and celestial guardian encounters",
    "necropolis city with undead civilization and death magic architecture",
    "primal jungle with oversized flora and ancient beast territories",
    "dimensional laboratory with portal experiments and reality manipulation",
    "cosmic void with star formations and celestial navigation",
    "entropy zone with decay effects and time acceleration",
    "harmony temple with balance magic and yin-yang energy flows",
    
    # ===== RAID DUNGEONS & BOSS AREAS (25 scenarios) =====
    "massive dragon lair with treasure horde and volcanic atmosphere",
    "ancient titan's chamber with colossal skeleton and epic scale",
    "demon lord's throne room with infernal architecture and lava moats",
    "corrupted world tree with twisted branches and nature magic gone wrong",
    "lich king's fortress with undead armies and necromantic power",
    "elemental lord's domain with swirling primal energies",
    "cosmic entity's realm with star-filled void and reality distortion",
    "fallen angel's cathedral with corrupted holy magic and divine architecture",
    "kraken's underwater domain with tentacles and oceanic pressure",
    "phoenix nest with eternal flames and rebirth magic cycles",
    "void dragon's dimension with space-time manipulation and cosmic breath",
    "ancient golem factory with mechanical armies and steam-powered machinery",
    "nightmare beast's dream realm with surreal horror landscapes",
    "elemental convergence point with all four elements in chaotic harmony",
    "time dragon's temporal lair with past and future simultaneously visible",
    "shadow empress's dark palace with living shadows and umbral magic",
    "crystal behemoth's cave with gem-encrusted walls and prismatic attacks",
    "storm giant's cloud fortress with lightning and wind manipulation",
    "corrupted unicorn's grove with twisted nature and dark rainbow effects",
    "ancient sphinx's pyramid chamber with riddles and knowledge trials",
    "void whale's cosmic belly with digestive nebulae and acid storms",
    "primordial turtle's shell world with continental-scale geography",
    "chaos dragon's reality storm with constantly shifting environments",
    "divine avatar's testing chamber with moral challenges and light trials",
    "entropy lord's decay palace with time acceleration and destruction magic",
    
    # ===== PVP BATTLEGROUNDS (20 scenarios) =====
    "arena colosseum with spectator stands and gladiator combat zones",
    "fortress siege battlefield with catapults and defensive walls",
    "capture-the-flag field with team bases and strategic chokepoints",
    "king-of-the-hill mountain with elevated position and tactical advantage",
    "bridge battle zone with narrow crossing and strategic positioning",
    "forest ambush area with hiding spots and guerrilla warfare terrain",
    "desert skirmish ground with sand dunes and visibility challenges",
    "frozen lake battlefield with slippery surfaces and ice magic",
    "lava pit arena with environmental hazards and fire damage zones",
    "ruins battleground with destructible cover and ancient magic",
    "sky platform combat with aerial maneuvering and fall damage",
    "underground tunnel warfare with close-quarters and ambush tactics",
    "magical duel circle with arcane enhancements and spell amplification",
    "ship-to-ship naval combat with cannons and boarding actions",
    "castle courtyard siege with multiple levels and defensive positions",
    "crystal cave PvP with light refraction and visibility tricks",
    "poison swamp battle with environmental damage and area denial",
    "gravity-shifting arena with wall-walking and 3D combat",
    "time-dilated battlefield with speed manipulation and temporal tactics",
    "elemental chaos zone with random magic effects and adaptive strategy",
    
    # ===== SOCIAL & TOWN HUBS (25 scenarios) =====
    "grand capital city plaza with multiple districts and heavy foot traffic",
    "auction house interior with bidding crowds and rare item displays",
    "guild hall meeting room with strategy planning and alliance discussions",
    "player housing district with customizable homes and neighborhood feel",
    "crafting marketplace with artisan NPCs and player-made goods",
    "tavern common room with players socializing and quest planning",
    "bank interior with vault security and wealth management NPCs",
    "library study area with lore research and knowledge sharing",
    "training grounds with players practicing and skill development",
    "mount stable with exotic creatures and riding practice areas",
    "festival grounds with seasonal events and celebration activities",
    "trading post with merchant caravans and exotic goods from distant lands",
    "portal hub with transportation to different zones and realms",
    "arena waiting room with competitors preparing for matches",
    "workshop district with crafting stations and material processing",
    "temple complex with multiple deities and blessing services",
    "player market with stalls and direct player-to-player trading",
    "embassy quarter with faction representatives and diplomatic missions",
    "academy campus with skill trainers and advanced learning",
    "harbor district with ships and oceanic travel options",
    "theater district with entertainment and cultural activities",
    "residential gardens with peaceful areas and social gatherings",
    "magic quarter with spell research and arcane knowledge sharing",
    "adventurer's quarter with quest boards and party formation",
    "merchant district with specialized shops and economic activities",
    
    # ===== SPECIAL EVENTS & SEASONAL (20 scenarios) =====
    "winter festival town with snow decorations and holiday NPCs",
    "harvest celebration with autumn colors and farming activities",
    "spring flower festival with blooming gardens and nature magic",
    "summer solstice gathering with sun magic and light celebrations",
    "halloween haunted area with spooky decorations and monster spawns",
    "valentine's love garden with romantic atmosphere and couple activities",
    "new year celebration with fireworks and resolution NPCs",
    "dragon boat festival with water races and aquatic competitions",
    "midsummer night's dream with fairy magic and whimsical atmosphere",
    "octoberfest celebration with ale, music, and tavern games",
    "cherry blossom viewing with pink petals and peaceful meditation",
    "carnival grounds with games, rides, and festive atmosphere",
    "masked ball event with formal wear and social dancing",
    "treasure hunt event with clues and hidden rewards",
    "cooking competition with chef NPCs and culinary challenges",
    "music festival with bard performances and rhythm games",
    "art exhibition with player creations and cultural appreciation",
    "sports tournament with various competitive activities",
    "mystery event with detective work and puzzle solving",
    "time capsule ceremony with historical significance and nostalgia"
]

def enhance_mmo_prompt(scenario):
    """Enhance scenario with MMO-specific visual elements"""
    base_style = "fantasy MMO concept art, vibrant colors, atmospheric lighting, detailed digital painting, cinematic composition"
    
    # Add MMO-specific elements based on scenario content
    scenario_lower = scenario.lower()
    
    if 'starter' in scenario_lower or 'newbie' in scenario_lower or 'beginner' in scenario_lower:
        mmo_elements = "welcoming atmosphere, tutorial UI elements, helpful NPCs, bright lighting, safe zone feeling"
    elif 'dungeon' in scenario_lower or 'cave' in scenario_lower or 'crypt' in scenario_lower:
        mmo_elements = "party-based content, loot containers, monster spawns, atmospheric shadows, dungeon crawler aesthetic"
    elif 'raid' in scenario_lower or 'boss' in scenario_lower or 'dragon' in scenario_lower:
        mmo_elements = "epic scale, dramatic lighting, multiple player positions, legendary loot, cinematic boss encounter"
    elif 'pvp' in scenario_lower or 'battle' in scenario_lower or 'arena' in scenario_lower:
        mmo_elements = "competitive atmosphere, strategic positions, team colors, balanced layout, esports aesthetic"
    elif 'town' in scenario_lower or 'city' in scenario_lower or 'hub' in scenario_lower:
        mmo_elements = "bustling activity, multiple NPCs, quest givers, social spaces, vibrant community feel"
    elif 'guild' in scenario_lower or 'social' in scenario_lower:
        mmo_elements = "player interaction spaces, customization options, community features, cooperative atmosphere"
    elif 'festival' in scenario_lower or 'event' in scenario_lower or 'celebration' in scenario_lower:
        mmo_elements = "special decorations, limited-time content, festive lighting, unique rewards, community gathering"
    elif 'craft' in scenario_lower or 'market' in scenario_lower or 'shop' in scenario_lower:
        mmo_elements = "player economy, item displays, trading interfaces, merchant NPCs, economic hub"
    else:
        mmo_elements = "open world exploration, quest opportunities, resource gathering, adventure awaiting"
    
    return f"{scenario}, {base_style}, {mmo_elements}, professional MMORPG game art"

def generate_mmo_batch_images(scenarios=None, batch_size=10, delay_between_batches=45):
    """
    Generate MMO-style images with enhanced prompts and conservative GPU usage
    
    Args:
        scenarios: List of scenario descriptions. If None, uses MMO_RPG_SCENARIOS
        batch_size: Number of images to generate before taking a break
        delay_between_batches: Seconds to wait between batches (reduced for faster generation)
    """
    if scenarios is None:
        scenarios = MMO_RPG_SCENARIOS
    
    print(f"🎮 Starting MMO batch generation of {len(scenarios)} images")
    print(f"Batch size: {batch_size}, Delay between batches: {delay_between_batches}s")
    
    # Check ComfyUI status first
    if not check_comfyui_status():
        print("❌ ComfyUI is not running! Please start ComfyUI first.")
        return
    
    successful_generations = []
    failed_generations = []
    
    total_batches = (len(scenarios) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(scenarios))
        batch_scenarios = scenarios[start_idx:end_idx]
        
        print(f"\n🎨 Starting MMO Batch {batch_num + 1}/{total_batches}")
        print(f"Generating images {start_idx + 1} to {end_idx} of {len(scenarios)}")
        
        for i, scenario in enumerate(batch_scenarios, start_idx + 1):
            print(f"\n[{i}/{len(scenarios)}] Processing MMO scene: {scenario[:80]}...")
            
            try:
                # Enhance the scenario with MMO-specific elements
                enhanced_prompt = enhance_mmo_prompt(scenario)
                result = generate_image_from_text(enhanced_prompt)
                
                if result:
                    successful_generations.append((scenario, result))
                    print(f"✅ Success: {result}")
                else:
                    failed_generations.append(scenario)
                    print(f"❌ Failed to generate image")
                
                # Small delay between individual generations
                time.sleep(1.5)  # Reduced delay for faster generation
                
            except KeyboardInterrupt:
                print(f"\n⚠️ Generation interrupted by user at scenario {i}")
                save_mmo_generation_manifest(successful_generations, failed_generations)
                return
            except Exception as e:
                print(f"❌ Error generating image for scenario {i}: {e}")
                failed_generations.append(scenario)
        
        # Take a break between batches (except for the last batch)
        if batch_num < total_batches - 1:
            print(f"\n⏱️ Taking {delay_between_batches}s break to prevent GPU overheating...")
            for remaining in range(delay_between_batches, 0, -5):
                print(f"Resuming in {remaining}s...", end="\r")
                time.sleep(5)
            print(" " * 20)  # Clear the countdown line
    
    # Generate summary report
    print(f"\n{'='*70}")
    print(f"MMO BATCH GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Successful generations: {len(successful_generations)}")
    print(f"❌ Failed generations: {len(failed_generations)}")
    print(f"📊 Success rate: {len(successful_generations)/len(scenarios)*100:.1f}%")
    
    if failed_generations:
        print(f"\n⚠️ Failed scenarios:")
        for i, scenario in enumerate(failed_generations, 1):
            print(f"   {i}. {scenario[:100]}...")
    
    # Save a manifest of all generated images
    save_mmo_generation_manifest(successful_generations, failed_generations)

def save_mmo_generation_manifest(successful, failed):
    """Save a JSON manifest of all generated MMO images"""
    manifest = {
        "generation_type": "MMO_RPG",
        "generation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_scenarios": len(MMO_RPG_SCENARIOS),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "categories": {
            "starter_zones": 30,
            "low_level_zones": 35,
            "mid_level_dungeons": 30,
            "high_level_zones": 35,
            "raid_dungeons": 25,
            "pvp_battlegrounds": 20,
            "social_hubs": 25,
            "special_events": 20
        },
        "successful_images": [
            {
                "scenario": scenario,
                "image_path": path,
                "filename": os.path.basename(path)
            }
            for scenario, path in successful
        ],
        "failed_scenarios": failed
    }
    
    manifest_path = "static/images/mmo_generation_manifest.json"
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"📋 MMO Generation manifest saved to: {manifest_path}")

def generate_by_mmo_category(categories=None, batch_size=8):
    """Generate images for specific MMO categories only"""
    category_map = {
        "starter": MMO_RPG_SCENARIOS[0:30],      # Starter zones
        "lowlevel": MMO_RPG_SCENARIOS[30:65],    # Low-level zones  
        "dungeons": MMO_RPG_SCENARIOS[65:95],    # Mid-level dungeons
        "highlevel": MMO_RPG_SCENARIOS[95:130],  # High-level zones
        "raids": MMO_RPG_SCENARIOS[130:155],     # Raid dungeons & bosses
        "pvp": MMO_RPG_SCENARIOS[155:175],       # PVP battlegrounds
        "social": MMO_RPG_SCENARIOS[175:200],    # Social & town hubs
        "events": MMO_RPG_SCENARIOS[200:220]     # Special events & seasonal
    }
    
    if categories is None:
        print("Available MMO categories:")
        for cat, scenarios in category_map.items():
            print(f"  {cat}: {len(scenarios)} scenarios")
        return
    
    scenarios_to_generate = []
    for category in categories:
        if category in category_map:
            scenarios_to_generate.extend(category_map[category])
            print(f"Added {len(category_map[category])} scenarios from '{category}' category")
        else:
            print(f"Warning: Unknown category '{category}'")
    
    if scenarios_to_generate:
        generate_mmo_batch_images(scenarios_to_generate, batch_size)

if __name__ == "__main__":
    print("🎮 MMO RPG Image Batch Generator")
    print("=" * 60)
    print("Designed for MMORPG-style fantasy content")
    
    # Ask user what they want to do
    print("\nOptions:")
    print("1. Generate all 220 MMO images (full collection)")
    print("2. Generate specific MMO categories only")
    print("3. Test with 10 sample MMO images")
    print("4. Quick starter zone generation (30 images)")
    print("5. Essential MMO zones only (100 core images)")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        # Generate all MMO images with conservative settings
        generate_mmo_batch_images(batch_size=10, delay_between_batches=45)
    
    elif choice == "2":
        print("\nAvailable MMO categories:")
        print("starter, lowlevel, dungeons, highlevel, raids, pvp, social, events")
        cats = input("Enter categories (comma-separated): ").strip().split(",")
        cats = [c.strip() for c in cats if c.strip()]
        generate_by_mmo_category(cats)
    
    elif choice == "3":
        # Test with diverse sample from each category
        test_scenarios = [
            MMO_RPG_SCENARIOS[0],    # Starter
            MMO_RPG_SCENARIOS[35],   # Low-level
            MMO_RPG_SCENARIOS[70],   # Dungeon
            MMO_RPG_SCENARIOS[105],  # High-level
            MMO_RPG_SCENARIOS[135],  # Raid
            MMO_RPG_SCENARIOS[160],  # PVP
            MMO_RPG_SCENARIOS[180],  # Social
            MMO_RPG_SCENARIOS[205],  # Events
            MMO_RPG_SCENARIOS[50],   # Extra variety
            MMO_RPG_SCENARIOS[150]   # Extra variety
        ]
        generate_mmo_batch_images(test_scenarios, batch_size=5, delay_between_batches=30)
    
    elif choice == "4":
        # Just starter zones for quick setup
        starter_scenarios = MMO_RPG_SCENARIOS[0:30]
        generate_mmo_batch_images(starter_scenarios, batch_size=8, delay_between_batches=30)
    
    elif choice == "5":
        # Essential zones only - mix of most important areas
        essential_scenarios = (
            MMO_RPG_SCENARIOS[0:15] +      # Key starter areas
            MMO_RPG_SCENARIOS[30:50] +     # Important low-level zones
            MMO_RPG_SCENARIOS[65:85] +     # Core dungeons
            MMO_RPG_SCENARIOS[95:110] +    # Key high-level zones
            MMO_RPG_SCENARIOS[130:145] +   # Important raids
            MMO_RPG_SCENARIOS[175:185]     # Essential social hubs
        )
        print(f"Generating {len(essential_scenarios)} essential MMO images...")
        generate_mmo_batch_images(essential_scenarios, batch_size=10, delay_between_batches=40)
    
    else:
        print("Invalid choice. Exiting...")