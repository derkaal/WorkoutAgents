// Training Agent (Mike Lowrey) - Confident, humorous workout generator
export class MikeLowrey {
  private personality = {
    tone: 'confident',
    humor: 'high',
    catchphrases: [
      "Let's get after it!",
      "Time to show those muscles who's boss!",
      "We're about to turn up the heat!",
      "Ready to crush this workout?"
    ]
  };

  async generateWorkout(preferences: any, feedback?: string[]): Promise<any> {
    // This would normally call GPT-4o API
    // For now, returning mock data with Mike's personality
    
    const workoutTypes = ['Core + Hip', 'Upper Body + Core', 'Hip + Yoga', 'Running'];
    const randomType = workoutTypes[Math.floor(Math.random() * workoutTypes.length)];
    
    return {
      type: randomType,
      duration: 30,
      intro: this.generateIntro(randomType),
      exercises: this.generateExercises(randomType),
      mikeQuote: this.getRandomCatchphrase()
    };
  }

  private generateIntro(type: string): string {
    const intros = {
      'Core + Hip': "Alright, we're hitting the core and hips today! These muscles are your powerhouse - let's light them up for a full 30 minutes!",
      'Upper Body + Core': "Time to build some serious upper body strength! Your core's coming along for the ride too! 30 minutes of pure fire!",
      'Hip + Yoga': "Today we're flowing and stretching those hips. Don't let the yoga fool you - this 30-minute session is going to be transformative!",
      'Running': "Lace up those shoes! We're taking it to the streets for a solid 30-minute session. Let's see what you've got!"
    };
    return intros[type] || "Let's get this 30-minute workout started!";
  }

  private generateExercises(type: string): any[] {
    const exercises = {
      'Core + Hip': [
        { name: 'Warm-up Hip Circles', duration: 120, instruction: "Start easy! Get those hips moving and blood flowing!", image: '/images/hip-circles.jpg' },
        { name: 'Glute Bridges', duration: 180, instruction: "Drive those hips up! Squeeze those glutes like you're cracking walnuts!", image: '/images/glute-bridges.jpg' },
        { name: 'Plank Hold', duration: 120, instruction: "Hold it steady! Your core should be working harder than a detective on a case!", image: '/images/plank.jpg' },
        { name: 'Fire Hydrants', duration: 150, instruction: "Light up those glutes! Keep that core tight throughout!", image: '/images/fire-hydrants.jpg' },
        { name: 'Dead Bug', duration: 180, instruction: "Slow and controlled! Your core should be working overtime here!", image: '/images/dead-bug.jpg' },
        { name: 'Hip Flexor Stretch', duration: 120, instruction: "Open up those tight hips! Feel that stretch working!", image: '/images/hip-flexor-stretch.jpg' },
        { name: 'Bird Dog', duration: 150, instruction: "Balance and control! Show me that core stability!", image: '/images/bird-dog.jpg' },
        { name: 'Side Plank (Left)', duration: 90, instruction: "Fire up that left side! Keep those hips stacked!", image: '/images/side-plank.jpg' },
        { name: 'Side Plank (Right)', duration: 90, instruction: "Now the right side! Balance is everything!", image: '/images/side-plank.jpg' },
        { name: 'Glute Bridge Pulses', duration: 120, instruction: "Pulse it out! Those glutes should be burning now!", image: '/images/glute-bridges.jpg' },
        { name: 'Russian Twists', duration: 150, instruction: "Twist and burn! Feel that core working!", image: '/images/russian-twists.jpg' },
        { name: 'Hip Circles Cooldown', duration: 120, instruction: "Cool it down! Nice and easy circles to finish strong!", image: '/images/hip-circles.jpg' }
      ],
      'Upper Body + Core': [
        { name: 'Arm Circles Warm-up', duration: 120, instruction: "Get those shoulders ready! Big circles, then small ones!", image: '/images/arm-circles.jpg' },
        { name: 'Push-ups', duration: 180, instruction: "Push the floor away! Show it who's the boss around here!", image: '/images/push-ups.jpg' },
        { name: 'Dumbbell Rows', duration: 150, instruction: "Pull those weights like you're starting a motorcycle!", image: '/images/dumbbell-rows.jpg' },
        { name: 'Plank to Downward Dog', duration: 120, instruction: "Flow between positions! Keep that core engaged!", image: '/images/plank-to-dog.jpg' },
        { name: 'Dumbbell Shoulder Press', duration: 150, instruction: "Press it up with authority! Control the weight!", image: '/images/dumbbell-press.jpg' },
        { name: 'Mountain Climbers', duration: 120, instruction: "Fast feet, tight core! Climb that mountain, champ!", image: '/images/mountain-climbers.jpg' },
        { name: 'Dumbbell Bicep Curls', duration: 120, instruction: "Curl with control! Feel those biceps working!", image: '/images/bicep-curls.jpg' },
        { name: 'Tricep Dips', duration: 150, instruction: "Lower and push! Those triceps are going to feel this!", image: '/images/tricep-dips.jpg' },
        { name: 'Wall Handstand Hold', duration: 90, instruction: "Use that wall! Build some serious shoulder strength!", image: '/images/wall-handstand.jpg' },
        { name: 'Russian Twists', duration: 120, instruction: "Twist and shout! Feel that core burn!", image: '/images/russian-twists.jpg' },
        { name: 'Push-up to T', duration: 150, instruction: "Push up and rotate! Full body engagement!", image: '/images/pushup-t.jpg' },
        { name: 'Shoulder Stretch', duration: 120, instruction: "Stretch it out! Your shoulders earned this recovery!", image: '/images/shoulder-stretch.jpg' }
      ],
      'Hip + Yoga': [
        { name: 'Centering Breath', duration: 120, instruction: "Find your center. Deep breaths to start our journey!", image: '/images/breathing.jpg' },
        { name: "Child's Pose", duration: 180, instruction: "Breathe deep and stretch it out. Even warriors need recovery time!", image: '/images/childs-pose.jpg' },
        { name: 'Cat-Cow Flow', duration: 150, instruction: "Flow like water, strong like steel. Let those hips move!", image: '/images/cat-cow.jpg' },
        { name: 'Downward Dog', duration: 120, instruction: "Strong foundation! Feel that whole body stretch!", image: '/images/downward-dog.jpg' },
        { name: 'Low Lunge (Left)', duration: 150, instruction: "Deep lunge! Open up that left hip flexor!", image: '/images/low-lunge.jpg' },
        { name: 'Low Lunge (Right)', duration: 150, instruction: "Switch sides! Balance those hips out!", image: '/images/low-lunge.jpg' },
        { name: 'Pigeon Pose (Left)', duration: 180, instruction: "Deep stretch time! Let that left hip release the tension!", image: '/images/pigeon-pose.jpg' },
        { name: 'Pigeon Pose (Right)', duration: 180, instruction: "Right side now! Feel that deep hip opening!", image: '/images/pigeon-pose.jpg' },
        { name: 'Happy Baby', duration: 150, instruction: "Rock and roll! Let those hips open up naturally!", image: '/images/happy-baby.jpg' },
        { name: 'Supine Twist (Left)', duration: 120, instruction: "Gentle twist to the left! Release that lower back!", image: '/images/supine-twist.jpg' },
        { name: 'Supine Twist (Right)', duration: 120, instruction: "Twist to the right! Balance is everything!", image: '/images/supine-twist.jpg' },
        { name: 'Final Savasana', duration: 150, instruction: "Complete rest. You've earned this peaceful moment!", image: '/images/savasana.jpg' }
      ],
      'Running': [
        { name: 'Dynamic Warm-up', duration: 300, instruction: "Get those legs ready! High knees, butt kicks, leg swings!", image: '/images/dynamic-warmup.jpg' },
        { name: 'Easy Pace Run', duration: 600, instruction: "Find your rhythm! Comfortable pace to start!", image: '/images/easy-run.jpg' },
        { name: 'Tempo Intervals', duration: 480, instruction: "Pick up the pace! 2 minutes hard, 1 minute easy, repeat!", image: '/images/tempo-run.jpg' },
        { name: 'Recovery Jog', duration: 300, instruction: "Bring it back down! Let your heart rate settle!", image: '/images/recovery-jog.jpg' },
        { name: 'Cool Down Walk', duration: 300, instruction: "Walk it out! Let your body gradually return to rest!", image: '/images/cool-down-walk.jpg' },
        { name: 'Post-Run Stretching', duration: 210, instruction: "Stretch those legs! Hip flexors, calves, and hamstrings!", image: '/images/post-run-stretch.jpg' }
      ]
    };

    return exercises[type] || [];
  }

  private getRandomCatchphrase(): string {
    return this.personality.catchphrases[
      Math.floor(Math.random() * this.personality.catchphrases.length)
    ];
  }

  generateInstructions(exerciseName: string): string {
    const instructions = {
      'Glute Bridges': "Lie on your back, feet flat. Drive those hips up! Squeeze those glutes like you're cracking walnuts!",
      'Plank': "Keep that body straight as an arrow. Core tight, breathe steady!",
      'Push-ups': "Hands shoulder-width apart. Lower with control, push up with power!",
      "Child's Pose": "Sit back on your heels, arms forward. Find your zen, champ!",
      'Hip Circles': "Standing tall, hands on hips. Make smooth circles!",
      'Dead Bug': "Lie on back, arms up. Opposite arm and leg movements!",
      'Fire Hydrants': "On all fours, lift that leg to the side. Fire it up!",
      'Bird Dog': "Opposite arm and leg out. Hold that balance!",
      'Mountain Climbers': "Plank position, run those knees in fast!",
      'Dumbbell Rows': "Bent over, pull that weight to your ribs!",
      'Russian Twists': "Seated, lean back, twist side to side!",
      'Cat-Cow': "On all fours, arch and round that spine!",
      'Hip Flexor Stretch': "Lunge position, push those hips forward!",
      'Pigeon Pose': "One leg forward, sit deep into that stretch!",
      'Downward Dog': "Hands and feet down, make an upside-down V!",
      'Happy Baby': "Lie on back, grab your feet, rock gently!",
      'Dynamic Warm-up': "Get moving! High knees, butt kicks, prepare those muscles!",
      'Main Run': "Find your rhythm and maintain it. You've got this!",
      'Cool Down Walk': "Easy pace, let your body recover gradually!"
    };
    
    return instructions[exerciseName] || "Give it your all! You've got this!";
  }
}
