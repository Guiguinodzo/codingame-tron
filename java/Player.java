import java.util.*;
import java.io.*;
import java.math.*;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
class Player {
   

    public static void main(String args[]) {
        Scanner in = new Scanner(System.in);
        Grid grid = new Grid(30,20);
        int count = 0;
        // My coordinates
        Coord me = new Coord(-1, -1);
        // game loop
        String choice = Direction.LEFT;
        Stack<String> moves = new Stack<String>();
        
        while (true) {
            long before = System.currentTimeMillis();
            int N = in.nextInt(); // total number of players (2 to 4).
            int P = in.nextInt(); // your player number (0 to 3).
            in.nextLine();
            for (int i = 0; i < N; i++) {
                // player is i
                int X0 = in.nextInt(); // starting X coordinate of lightcycle (or -1)
                int Y0 = in.nextInt(); // starting Y coordinate of lightcycle (or -1)
                int X1 = in.nextInt(); // starting X coordinate of lightcycle (can be the same as X0 if you play before this player)
                int Y1 = in.nextInt(); // starting Y coordinate of lightcycle (can be the same as Y0 if you play before this player)
                in.nextLine();
                if(X0 == -1 && Y0 == -1) { // player i is dead
                    System.err.println("Player "+i+" is dead!");
                    grid.death(i);
                } else {
                    if(count == 0) { //First turn, we must register the tail
                        grid.set(new Coord(X0,Y0),i, i==P);
                    }
                   grid.set(new Coord(X1,Y1),i, i==P);
                }
                
                if( i  == P ) {
                    me.x = X1;
                    me.y = Y1;
                }
            }

//            grid.print();
            boolean chosen = false;
            
            // Can we keep the same direction?
            boolean nextMovePossible = grid.isFree(me,choice);
           
            // Keep the same direction as long as possible
//            if(!nextMovePossible)
            choice = grid.bestDir(me, choice);
            
            if(moves.isEmpty() || !choice.equals(moves.peek())) {
                moves.add(choice);
            }
            System.out.println(choice); // A single line with UP, DOWN, LEFT or RIGHT
            count+=1;

            System.err.println("Computed in "+(System.currentTimeMillis()-before)+"ms");
        }
    }
    
    public static class Direction {
        public static final String LEFT = "LEFT";
        public static final String RIGHT = "RIGHT";
        public static final String UP = "UP";
        public static final String DOWN = "DOWN";
        
        public static String opposite(String dir) {
            if(LEFT.equals(dir))
                return RIGHT;
            else if(RIGHT.equals(dir))
                return LEFT;
            else if(DOWN.equals(dir))
                return UP;
            else
                return DOWN;
        }
    }

    public static class Coord {
        public int x;
        public int y;
        public Coord(int x, int y) {
            this.x = x;
            this.y = y;
        }
         public Coord(Coord from) {
            this.x = from.x;
            this.y = from.y;
        }
       
        public Coord left() {
            return new Coord(x-1,y);
        }
        public Coord right() {
            return new Coord(x+1,y);
        }
        public Coord up() {
            return new Coord(x,y-1);
        }
        public Coord down() {
            return new Coord(x,y+1);
        }
        public ArrayList<Coord> nextTo() {
            ArrayList<Coord> next = new ArrayList<Coord>();
            next.add(up());
            next.add(down());
            next.add(left());
            next.add(right());
            return next;
        }
        public boolean equals(Coord c) {
            return c.x == x && c.y == y;
        }

        public int distance(Coord c) {
            return Math.abs(c.x-x) + Math.abs(c.y-y);
        }
        public String toString() {
            return "["+x+","+y+"]";
        }
    }

    public static class Challenger {
        public int number;
        public Coord tail;
        public Coord head;
        public String direction;
        public boolean me;

        public Challenger(int number, Coord tail, boolean me) {
            this.number = number;
            this.tail = tail;
            this.head = tail; 
            this.direction = Direction.LEFT;
            this.me = me;
        }

        public boolean isMe() {
            return me;
        }

        public void update(Coord newPos) {
            if (head.left().equals(newPos)) {
                direction =  Direction.LEFT;

            } else if (head.right().equals(newPos)) {
                direction =  Direction.RIGHT;
            
            } else if (head.up().equals(newPos)) {
                direction =  Direction.UP;
            
            } else {
                direction =  Direction.DOWN;
            }
            this.head = newPos;
        }

        public String toString() {
            return "{"+number+" : "+head+"}";
        }
    }
    
    public static class Grid {
        private static final int FREE = -1;
        private static final int EXCLUDED = 5; // set a free space to block, temporary
        private int width;
        private int height;
        private int[][] map;
        private HashMap<Integer,Challenger> players = new HashMap<Integer,Challenger>();
        public LinkedList<Coord> path = null;
        
        public Grid(int width, int height) {
            this.width = width;
            this.height = height;
            this.map = new int[width][height];
            init();
        }

        private void init() {
            for(int x = 0; x < width; x++) {
                for(int y = 0; y < height; y++) {
                    map[x][y] = FREE;
                }
            }
        }
        
        public void print() {
            for(int y = 0; y < height; y++) {
                for(int x = 0; x < width; x++) {
                    int v = map[x][y];
                    if(v == FREE) {
                        System.err.print(" . ");
                    } else if(v < 10) {
                        System.err.print(" "+map[x][y]+" ");
                    } else {
                        System.err.print(+map[x][y]+" ");
                    }
                }
                System.err.println();
            }
        }
        
        private boolean isFree(int x, int y) {
            return isFree(new Coord(x,y));
        }
        
        private boolean isFree(Coord coord) {
            return coord.x >= 0 && coord.x < 30 && coord.y >= 0 && coord.y < 20 && map[coord.x][coord.y] == FREE;
        }
        
         private boolean isFree(Coord from, String dir) {
            Coord coord = from;
            if(Direction.LEFT.equals(dir)) {
                coord = from.left();
            } else if(Direction.RIGHT.equals(dir)) {
                coord = from.right();
            } else if(Direction.UP.equals(dir)) {
                coord = from.up();
            } else if(Direction.DOWN.equals(dir)) {
                coord = from.down();
            }
            return isFree(coord);
        }
       
        public int get(Coord coord) {
            return map[coord.x][coord.y];
        }
        
        public void set(Coord coord, int player, boolean me) {
            map[coord.x][coord.y] = player;
            if(players.containsKey(Integer.valueOf(player))) {
                Challenger p = players.get(Integer.valueOf(player));
                p.update(coord);
            } else if(player != FREE) {
                Challenger p = new Challenger(player, coord, me);
                players.put(Integer.valueOf(player), p);
            }
        }

        public Challenger getPlayer(int player) {
            return players.get(Integer.valueOf(player));
        }
        
        public void death(int player) {
            if(players.containsKey(Integer.valueOf(player))) {
                for(int x = 0; x < width; x++) {
                    for(int y = 0; y < height; y++) {
                        if(map[x][y] == player)
                            map[x][y] = FREE;
                    }
                }
                players.remove(Integer.valueOf(player));
            }
        }
        
        public String bestDir(Coord me, String defaultDir) {
            String best = null;
            /*
            if(path == null || path.isEmpty() || !checkPath(path)) {
                //define path
            }
            Coord next = path.removeFirst();
            System.err.println("Going to "+next);
            best = goTo(me,next);
            */          

            best = mostOpenZone(me);
            if(best == null) {
                best = mostOpenZone(me, false);
            }

            if(best == null) {
                best = "Ain't no way but the hard way!";
            }
            return best;
        }

        private String longestLine(Coord me, String defaultDir) {
            // Left
            int leftDistance = 0;
            for(int x = me.x-1; x >= 0 && isFree(x,me.y); x--)
                leftDistance++;
            // Right
            int rightDistance = 0;
            for(int x = me.x+1; x < width && isFree(x,me.y); x++)
                rightDistance++;
            // Up
            int upDistance = 0;
            for(int y = me.y-1; y >= 0 && isFree(me.x,y); y--)
                upDistance++;
            // Left
            int downDistance = 0;
            for(int y = me.y+1; y < width && isFree(me.x,y); y++)
                downDistance++;
            String best = Direction.LEFT;
            int max = leftDistance;
            if(max < rightDistance || (max == rightDistance && Direction.RIGHT.equals(defaultDir))) {
                best = Direction.RIGHT;
                max = rightDistance;
            }
            if(max < upDistance || (max == upDistance && Direction.UP.equals(defaultDir))) {
                best = Direction.UP;
                max = upDistance;
            }
            if(max < downDistance || (max == downDistance && Direction.DOWN.equals(defaultDir))) {
                best = Direction.DOWN;
                max = downDistance;
            }
            return best;
        }

        private String mostOpenZone(Coord me) {
            return mostOpenZone(me,true);
        }

        private String mostOpenZone(Coord me, boolean excludeDeadEnds) {
            int[][] distances;
            int spaceUp = 0;
            int spaceDown = 0;
            int spaceLeft = 0;
            int spaceRight = 0;
            Coord up = me.up();
            Coord down = me.down();
            Coord left = me.left();
            Coord right = me.right();

            /*
            // Consider all possibilities of movement for players at once (ie every enemy will move in every direction next turn
            // Does not work well, obviously
            ArrayList<Coord> toFree = new ArrayList<Coord>();
            for(Challenger c : players.values()) {
                if(!c.isMe()) {
                    for(Coord coord : c.head.nextTo()) {
                        if(isFree(coord)) {
                            map[coord.x][coord.y] = c.number;
                            toFree.add(coord);
                        }
                    }
                }
            }
            */
            if(excludeDeadEnds) {
                int excluded = excludeDeadEnds(me);
                System.err.println("Excluded "+excluded+" positions");
                print();
            }

            if(isFree(up)) {
                map[up.x][up.y] = 1;
                distances = distances(up);
//                spaceUp = accessible(distances, me, 0);
                spaceUp = accessible(distances);
                map[up.x][up.y] = FREE;
            }
            if(isFree(down)) {
                map[down.x][down.y] = 1;
                distances = distances(down);
//                spaceDown = accessible(distances, me, 0);
                spaceDown = accessible(distances);
                map[down.x][down.y] = FREE;
            }
            if(isFree(left)) {
                map[left.x][left.y] = 1;
                distances = distances(left);
//                spaceLeft = accessible(distances, me, 0);
                spaceLeft = accessible(distances);
                map[left.x][left.y] = FREE;
            }
            if(isFree(right)) {
                map[right.x][right.y] = 1;
                distances = distances(right);
//                spaceRight = accessible(distances, me, 0);
                spaceRight = accessible(distances);
                map[right.x][right.y] = FREE;
            }
            /*
            // See above
            for(Iterator<Coord> it = toFree.iterator(); it.hasNext();) {
                Coord c = it.next();
                map[c.x][c.y] = FREE;
            }
            */

            if(excludeDeadEnds) {
                unexcludeAll();
            }

            //DEBUG
            System.err.println("Up: "+spaceUp+" Down: "+spaceDown+" Left: "+spaceLeft+" Right: "+spaceRight);
            
            int max = 0;
            ArrayList<String> choices = new ArrayList<String>(4);
            if(spaceUp >= max) {
                if(spaceUp > max) {
                    choices.clear();
                    max = spaceUp;
                }
                choices.add(Direction.UP);
            }
            if(spaceDown >= max) {
                if(spaceDown > max) {
                    choices.clear();
                    max = spaceDown;
                }
                choices.add(Direction.DOWN);
            }
            if(spaceLeft >= max) {
                if(spaceLeft > max) {
                    choices.clear();
                    max = spaceLeft;
                }
                choices.add(Direction.LEFT);
            }
            if(spaceRight >= max) {
                if(spaceRight > max) {
                    choices.clear();
                    max = spaceRight;
                }
                choices.add(Direction.RIGHT);
            }
            if(max > 0) {
                //return chooseOne(choices);
                return choices.get(0);
            } else {
                return null; // no relevant choice
            }
        }

        private static String chooseOne(ArrayList<String> possibilities) {
            Random rand = new Random();
            String choice = null;
            if(!possibilities.isEmpty()) {
                choice = possibilities.get(rand.nextInt(possibilities.size()));
            }
            return choice;
        }

        
        private String chooseRandom(Coord me) {
            ArrayList<String> list = new ArrayList<String>(4);
            if(isFree(me.left())) {
                list.add(Direction.LEFT);
            }
            if(isFree(me.right())) {
                list.add(Direction.RIGHT);
            }
            if(isFree(me.down())) {
                list.add(Direction.DOWN);
            }
            if(isFree(me.up())) {
                list.add(Direction.UP);
            }
            return chooseOne(list);
        }

        private int[][] distances(Coord me) {
            int distances[][] = new int[width][height];
            for(int x = 0; x < width; x++) {
                for(int y = 0;y < height; y++) {
                    distances[x][y] = width*height+1;
                }
            }
            doDistances(distances, me, 0);
            return distances;
        }

        private void doDistances(int[][] distances, Coord c, int d) {
            if((d==0 || isFree(c)) && distances[c.x][c.y] > d) {
                distances[c.x][c.y] = d;
                doDistances(distances, c.up(), d+1);
                doDistances(distances, c.down(), d+1);
                doDistances(distances, c.left(), d+1);
                doDistances(distances, c.right(), d+1);
            }
        }

        private int excludeDeadEnds(Coord me) {
            int myNum = map[me.x][me.y];
            map[me.x][me.y] = FREE;
            Coord c = new Coord(-1,-1);
            int excluded = 0;
            for(int x=0; x<width; x++) {
                c.x = x;
                for(int y = 0;y < height; y++) {
                    c.y = y;
                    excluded += doExcludeDeadEnds(c);
                }
            }
            map[me.x][me.y] = myNum;
            return excluded;
        }

        private int doExcludeDeadEnds(Coord c) {
            int excluded = 0;
            if(isFree(c)) {
                int nbPoss = 0;
                Coord up = c.up();
                Coord down = c.down();
                Coord left = c.left();
                Coord right = c.right();
                if(isFree(up))
                    nbPoss++;
                if(isFree(down))
                    nbPoss++;
                if(isFree(left))
                    nbPoss++;
                if(isFree(right))
                    nbPoss++;
                if(nbPoss < 2) {
                    map[c.x][c.y] = EXCLUDED;
                    excluded++;
                    excluded += doExcludeDeadEnds(up);
                    excluded += doExcludeDeadEnds(down);
                    excluded += doExcludeDeadEnds(left);
                    excluded += doExcludeDeadEnds(right);
                    
                }
            }
            return excluded;
        }
        
        private void unexcludeAll() {
            for(int x=0; x<width; x++) {
                for(int y = 0;y < height; y++) {
                    if(map[x][y] == EXCLUDED) {
                        map[x][y] = FREE;
                    }
                }
            }
        }

        private Coord farthestPoint(int[][] distances, Coord me) {
            int maxDist = 0;
            Coord maxCoord = me;
            for(int x = 0; x < width; x++) {
                for(int y = 0;y < height; y++) {
                    int d = distances[x][y];
                    if(d>maxDist && isFree(x,y) && distances[x][y] != width*height+1) {
                        maxDist = d;
                        maxCoord = new Coord(x,y);
                    }
                }
            }
            return maxCoord;
        }

        private Challenger nearestOpponent(Coord me) {
            //Remove enemies head from map
            for(Challenger p : players.values()) {
                if(!me.equals(p.head)) {
                    map[p.head.x][p.head.y] = FREE;
                }
            }
            int[][] distances = distances(me);
            Challenger chosen = null;
            int min = width*height+1;
            for(Challenger p : players.values()) {
                if(!me.equals(p.head)) {
                    int d = distances[p.head.x][p.head.y];
                    if(d < min) {
                        chosen = p;
                        min = d;
                    }
                }
            }
            //Put heads back
            for(Challenger p : players.values()) {
                if(!me.equals(p.head)) {
                    map[p.head.x][p.head.y] = p.number;
                }
            }
            return chosen;
        }

        private String goTo(Coord from, Coord to) {
            int dx = from.x - to.x;
            int dy = from.y - to.y;
            String hChoice = dx > 0 ? Direction.LEFT : Direction.RIGHT;
            String vChoice = dy > 0 ? Direction.UP : Direction.DOWN;
            return Math.abs(dx) > Math.abs(dy) ? hChoice : vChoice;
        }

        private LinkedList<Coord> path(int[][] distances, Coord to) {
            LinkedList<Coord> path = new LinkedList<Coord>();
            doPath(path, to, distances, distances[to.x][to.y]);
            return path;
        }

        private int accessible(int[][] distances) {
            int n = 0;
            for(int x = 0; x < width; x++) {
                for(int y = 0; y < height; y++) {
                    if(distances[x][y] < width*height+1) {
                        n++;
                    }
                }
            }
            return n;
        }
        private int accessible(int[][] distances, Coord c, int d) {
            final int MAX_WEIGHT = width*height+1;
            if(distances[c.x][c.y] != MAX_WEIGHT && distances[c.x][c.y] > d) {
                return 1 + accessible(distances, c.up(), distances[c.x][c.y])
                    +accessible(distances, c.left(), distances[c.x][c.y])
                    +accessible(distances, c.left(), distances[c.x][c.y])
                    +accessible(distances, c.left(), distances[c.x][c.y]);
            } else {
                return 0;
            }
        }

        private void doPath(LinkedList<Coord> path, Coord c, int[][] distances, int previousDist) {
            path.addFirst(c);
            Coord up = c.up();
            Coord down = c.down();
            Coord left = c.left();
            Coord right = c.right();
            Coord best = null;
            int minD = previousDist;
            if(isFree(up) && distances[up.x][up.y] < minD) {
                best = up;
                minD = distances[up.x][up.y];
            }
            if(isFree(down) && distances[down.x][down.y] < minD) {
                best = down;
                minD = distances[down.x][down.y];
            }
            if(isFree(right) && distances[right.x][right.y] < minD) {
                best = right;
                minD = distances[right.x][right.y];
            }
            if(isFree(left) && distances[left.x][left.y] < minD) {
                best = left;
                minD = distances[left.x][left.y];
            }
            if(best != null)
                doPath(path, best, distances, minD);
        }
        
        private boolean checkPath(LinkedList<Coord> path) {
            boolean ok = true;
            Iterator<Coord> it = path.iterator();
            for(; it.hasNext() && ok;) {
                Coord c = it.next();
                ok = isFree(c);
                if(!ok) {
                    System.err.println("Path blocked at "+c);
                }
            }
            return ok;
        }
    }
    
}
